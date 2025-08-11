
class ClusterTarget(BaseModel):
    group_id: int
    template_id: int

class ClusterRequest(BaseModel):
    name: str
    targets: List[ClusterTarget]

@router.post("/cluster")
def send_cluster_campaign(request: ClusterRequest, db: Session = Depends(get_db)):
    campaign = crud.create_campaign(db, name=request.name, mode="cluster", status="sending")

    total_sent = 0
    total_failed = 0

    for target in request.targets:
        group = crud.get_group(db, target.group_id)
        template = crud.get_template(db, target.template_id)

        if not group or not template:
            continue

        for contact in group.contacts:
            body = template.body.replace("{{name}}", f"{contact.first_name} {contact.last_name}".strip())
            body = body.replace("{{first_name}}", contact.first_name or "")
            body = body.replace("{{last_name}}", contact.last_name or "")
            body = body.replace("{{email}}", contact.email)

            success = email_sender.send_email(
                db=db,
                to_email=contact.email,
                subject=template.subject,
                body=body
            )

            status = "sent" if success else "failed"
            crud.create_delivery_log(db, campaign_id=campaign.id, contact_id=contact.id, status=status)
            if success:
                total_sent += 1
            else:
                total_failed += 1

    final_status = "completed" if total_failed == 0 else "completed_with_errors"
    crud.update_campaign_status(db, campaign.id, final_status)

    return {"message": f"Campaign '{request.name}' executed. Sent: {total_sent}, Failed: {total_failed}."}

from jinja2 import Template as JinjaTemplate
from fastapi import Form
import csv

@router.post("/personalized")
async def send_personalized_campaign(
    db: Session = Depends(get_db),
    name: str = Form(...),
    template_id: int = Form(...),
    file: UploadFile = File(...)
):
    if file.content_type != 'text/csv':
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a CSV.")

    campaign = crud.create_campaign(db, name=name, mode="personalized", status="sending")
    template = crud.get_template(db, template_id)
    if not template:
        crud.update_campaign_status(db, campaign.id, "failed")
        raise HTTPException(status_code=404, detail="Template not found")

    contents = await file.read()
    string_io = io.StringIO(contents.decode("utf-8"))
    reader = csv.DictReader(string_io)

    total_sent = 0
    total_failed = 0

    for row in reader:
        if 'email' not in row or not row['email']:
            continue

        jinja_subject = JinjaTemplate(template.subject)
        jinja_body = JinjaTemplate(template.body)

        rendered_subject = jinja_subject.render(row)
        rendered_body = jinja_body.render(row)

        success = email_sender.send_email(
            db=db,
            to_email=row['email'],
            subject=rendered_subject,
            body=rendered_body
        )

        contact = crud.get_contact_by_email(db, email=row['email'])
        if not contact:
            contact = crud.create_contact(db, schemas.ContactCreate(email=row['email'], first_name=row.get('first_name')))

        status = "sent" if success else "failed"
        crud.create_delivery_log(db, campaign_id=campaign.id, contact_id=contact.id, status=status)

        if success: total_sent += 1
        else: total_failed += 1

    final_status = "completed" if total_failed == 0 else "completed_with_errors"
    crud.update_campaign_status(db, campaign.id, final_status)

    return {"message": f"Campaign '{name}' executed. Sent: {total_sent}, Failed: {total_failed}."}
