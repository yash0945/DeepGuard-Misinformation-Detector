from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
import io
import csv

from .. import crud
from ..database import get_db

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
)

@router.get("/export")
def export_delivery_logs(db: Session = Depends(get_db)):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Log ID", "Campaign Name", "Contact Email", "Status", "Sent Time"])
    logs = crud.get_delivery_logs(db, limit=10000)
    for log in logs:
        writer.writerow([
            log.id,
            log.campaign.name,
            log.contact.email,
            log.status,
            log.sent_time.isoformat()
        ])
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=delivery_logs.csv"}
    )

@router.get("/campaigns")
def get_campaigns_for_report(db: Session = Depends(get_db)):
    return crud.get_campaigns(db, limit=100)
