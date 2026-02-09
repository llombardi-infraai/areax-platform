import json
import csv
import io
import zipfile
from typing import Optional
from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from models.data_control import Export, ExportStatus
from models.workspace import Workspace
from models.project import Project
from models.document import Document
from models.ai import AIConversation, AIMessage
from models.audit import AuditLog


class ExportService:
    """Service for handling data exports."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def start_export(self, export_id: UUID) -> None:
        """Start an export job asynchronously."""
        # In production, this would queue a background job
        # For now, mark as processing
        result = await self.db.execute(
            select(Export).where(Export.id == export_id)
        )
        export = result.scalar_one_or_none()
        
        if export:
            export.status = ExportStatus.PROCESSING
            export.started_at = datetime.utcnow()
            await self.db.commit()
            
            # Simulate processing
            await self._process_export(export)
    
    async def _process_export(self, export: Export) -> None:
        """Process the export and generate file."""
        org_id = export.org_id
        filters = export.filters or {}
        
        # Gather data based on filters
        data = await self._gather_export_data(org_id, filters)
        
        # Generate file based on format
        if export.format.value == "json":
            file_content = json.dumps(data, indent=2, default=str).encode("utf-8")
        elif export.format.value == "csv":
            file_content = self._generate_csv(data)
        else:
            file_content = json.dumps(data, default=str).encode("utf-8")
        
        # Store file (in production, upload to S3/Spaces)
        # For now, just update status
        export.status = ExportStatus.COMPLETED
        export.file_size = len(file_content)
        export.completed_at = datetime.utcnow()
        export.file_path = f"exports/{export.id}.{export.format.value}"
        
        await self.db.commit()
    
    async def _gather_export_data(self, org_id: str, filters: dict) -> dict:
        """Gather data for export."""
        data = {
            "exported_at": datetime.utcnow().isoformat(),
            "organization_id": org_id,
            "workspaces": [],
            "projects": [],
            "documents": [],
            "conversations": [],
            "audit_logs": [],
        }
        
        # Export workspaces
        if filters.get("include_workspaces", True):
            result = await self.db.execute(
                select(Workspace).where(Workspace.org_id == org_id)
            )
            for ws in result.scalars().all():
                data["workspaces"].append({
                    "id": str(ws.id),
                    "name": ws.name,
                    "description": ws.description,
                    "status": ws.status.value,
                    "created_at": ws.created_at.isoformat(),
                })
        
        # Export projects
        if filters.get("include_projects", True):
            result = await self.db.execute(
                select(Project).where(Project.org_id == org_id)
            )
            for proj in result.scalars().all():
                data["projects"].append({
                    "id": str(proj.id),
                    "name": proj.name,
                    "description": proj.description,
                    "type": proj.type.value,
                    "status": proj.status.value,
                    "created_at": proj.created_at.isoformat(),
                })
        
        # Export documents
        if filters.get("include_documents", True):
            result = await self.db.execute(
                select(Document).where(Document.org_id == org_id)
            )
            for doc in result.scalars().all():
                data["documents"].append({
                    "id": str(doc.id),
                    "title": doc.title,
                    "type": doc.type.value,
                    "status": doc.status.value,
                    "created_at": doc.created_at.isoformat(),
                })
        
        # Export conversations (if allowed)
        if filters.get("include_conversations", False):
            result = await self.db.execute(
                select(AIConversation).where(AIConversation.org_id == org_id)
            )
            for conv in result.scalars().all():
                data["conversations"].append({
                    "id": str(conv.id),
                    "title": conv.title,
                    "status": conv.status.value,
                    "created_at": conv.created_at.isoformat(),
                })
        
        # Export audit logs
        if filters.get("include_audit_logs", True):
            result = await self.db.execute(
                select(AuditLog).where(AuditLog.org_id == org_id)
            )
            for log in result.scalars().all():
                data["audit_logs"].append({
                    "id": str(log.id),
                    "action": log.action.value,
                    "resource_type": log.resource_type,
                    "severity": log.severity.value,
                    "created_at": log.created_at.isoformat(),
                })
        
        return data
    
    def _generate_csv(self, data: dict) -> bytes:
        """Generate CSV export."""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write summary
        writer.writerow(["Export Summary"])
        writer.writerow(["Exported At", data.get("exported_at")])
        writer.writerow(["Organization ID", data.get("organization_id")])
        writer.writerow([])
        
        # Write workspaces
        if data.get("workspaces"):
            writer.writerow(["Workspaces"])
            writer.writerow(["ID", "Name", "Status", "Created At"])
            for ws in data["workspaces"]:
                writer.writerow([ws["id"], ws["name"], ws["status"], ws["created_at"]])
            writer.writerow([])
        
        # Write projects
        if data.get("projects"):
            writer.writerow(["Projects"])
            writer.writerow(["ID", "Name", "Type", "Status", "Created At"])
            for proj in data["projects"]:
                writer.writerow([proj["id"], proj["name"], proj["type"], proj["status"], proj["created_at"]])
            writer.writerow([])
        
        return output.getvalue().encode("utf-8")
    
    async def get_download_url(self, export_id: UUID) -> Optional[str]:
        """Generate a presigned download URL for an export."""
        result = await self.db.execute(
            select(Export).where(Export.id == export_id)
        )
        export = result.scalar_one_or_none()
        
        if not export or export.status != ExportStatus.COMPLETED:
            return None
        
        # In production, generate presigned S3/Spaces URL
        # For now, return a placeholder
        return f"/api/v1/exports/{export_id}/download?token=temp"
