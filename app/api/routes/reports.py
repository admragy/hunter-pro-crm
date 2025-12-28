"""
Reports API Routes
PDF & Excel report generation
"""

from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel
from typing import Dict, List, Any, Optional

from app.services.report_service import ReportService, get_report_service

router = APIRouter(prefix="/api/reports", tags=["reports"])


# ==================== SCHEMAS ====================

class GeneratePDFReport(BaseModel):
    title: str
    data: Dict[str, Any]
    charts: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None


class GenerateExcelReport(BaseModel):
    title: str
    sheets: Dict[str, List[Dict[str, Any]]]
    metadata: Optional[Dict[str, Any]] = None


# ==================== ENDPOINTS ====================

@router.post("/pdf")
async def generate_pdf(
    data: GeneratePDFReport,
    reports: ReportService = Depends(get_report_service)
):
    """
    Generate custom PDF report
    """
    pdf_bytes = await reports.generate_pdf_report(
        title=data.title,
        data=data.data,
        charts=data.charts,
        metadata=data.metadata
    )
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={data.title}.pdf"
        }
    )


@router.post("/excel")
async def generate_excel(
    data: GenerateExcelReport,
    reports: ReportService = Depends(get_report_service)
):
    """
    Generate Excel report with multiple sheets
    """
    excel_bytes = await reports.generate_excel_report(
        title=data.title,
        sheets=data.sheets,
        metadata=data.metadata
    )
    
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={data.title}.xlsx"
        }
    )


@router.get("/dashboard/pdf")
async def download_dashboard_report(
    period: str = "last_30_days",
    reports: ReportService = Depends(get_report_service)
):
    """
    Download comprehensive dashboard PDF report
    """
    pdf_bytes = await reports.generate_dashboard_report(period)
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=dashboard_report_{period}.pdf"
        }
    )
