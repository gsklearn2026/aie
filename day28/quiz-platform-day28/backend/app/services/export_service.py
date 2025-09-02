import pandas as pd
import json
import xml.etree.ElementTree as ET
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import io
import uuid
import os
import gzip
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Generator
import asyncio
import aiofiles
from sqlalchemy.orm import Session
from sqlalchemy import text

from ..models.export_models import ExportJob, ExportStatus, ExportFormat
from ..models.quiz_models import QuizResult, QuestionAnalytics
from ..config.redis_config import redis_client
from ..utils.ai_insights import AIInsightsGenerator

class ExportService:
    def __init__(self, db: Session):
        self.db = db
        self.ai_insights = AIInsightsGenerator()
        
    async def create_export_job(self, request: Dict[str, Any], user_id: str) -> str:
        """Create a new export job"""
        job_id = str(uuid.uuid4())
        
        # Create database record
        export_job = ExportJob(
            job_id=job_id,
            user_id=user_id,
            export_format=request['format'],
            status=ExportStatus.QUEUED,
            parameters=json.dumps(request)
        )
        
        self.db.add(export_job)
        self.db.commit()
        
        # Queue job for processing
        redis_client.lpush("export_queue", job_id)
        
        return job_id
    
    async def process_export_job(self, job_id: str):
        """Process export job asynchronously"""
        # Get job from database
        job = self.db.query(ExportJob).filter(ExportJob.job_id == job_id).first()
        if not job:
            return
            
        try:
            # Update status to processing
            job.status = ExportStatus.PROCESSING
            self.db.commit()
            
            # Parse parameters
            params = json.loads(job.parameters)
            
            # Get data based on filters
            data = await self._get_export_data(params)
            job.total_records = len(data)
            self.db.commit()
            
            # Generate export file
            file_path = await self._generate_export_file(
                data, job.export_format, params, job_id
            )
            
            # Update job with completion details
            job.status = ExportStatus.COMPLETED
            job.file_path = file_path
            job.file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            job.completed_at = datetime.utcnow()
            job.progress = 100.0
            job.processed_records = job.total_records
            self.db.commit()
            
        except Exception as e:
            job.status = ExportStatus.FAILED
            job.error_message = str(e)
            self.db.commit()
    
    async def _get_export_data(self, params: Dict[str, Any]) -> List[Dict]:
        """Get data for export based on parameters"""
        query = self.db.query(QuizResult)
        
        # Apply filters
        if 'filters' in params:
            filters = params['filters']
            if 'user_id' in filters:
                query = query.filter(QuizResult.user_id == filters['user_id'])
            if 'quiz_id' in filters:
                query = query.filter(QuizResult.quiz_id == filters['quiz_id'])
            if 'subject_area' in filters:
                query = query.filter(QuizResult.subject_area == filters['subject_area'])
        
        # Apply date range
        if 'date_range' in params:
            date_range = params['date_range']
            if 'start_date' in date_range:
                start_date = datetime.fromisoformat(date_range['start_date'])
                query = query.filter(QuizResult.completed_at >= start_date)
            if 'end_date' in date_range:
                end_date = datetime.fromisoformat(date_range['end_date'])
                query = query.filter(QuizResult.completed_at <= end_date)
        
        results = query.all()
        
        # Convert to dictionaries and add AI insights
        data = []
        for result in results:
            record = {
                'id': result.id,
                'user_id': result.user_id,
                'quiz_id': result.quiz_id,
                'score': result.score,
                'total_questions': result.total_questions,
                'correct_answers': result.correct_answers,
                'time_taken': result.time_taken,
                'difficulty_level': result.difficulty_level,
                'subject_area': result.subject_area,
                'completed_at': result.completed_at.isoformat()
            }
            
            # Add AI insights if requested
            if params.get('include_ai_insights', True):
                insights = await self.ai_insights.generate_insights(record)
                record.update(insights)
            
            data.append(record)
        
        return data
    
    async def _generate_export_file(
        self, 
        data: List[Dict], 
        format: ExportFormat, 
        params: Dict[str, Any],
        job_id: str
    ) -> str:
        """Generate export file in specified format"""
        os.makedirs("exports", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == ExportFormat.CSV:
            return await self._generate_csv(data, job_id, timestamp)
        elif format == ExportFormat.JSON:
            return await self._generate_json(data, job_id, timestamp)
        elif format == ExportFormat.XML:
            return await self._generate_xml(data, job_id, timestamp)
        elif format == ExportFormat.PDF:
            return await self._generate_pdf(data, job_id, timestamp)
        elif format == ExportFormat.EXCEL:
            return await self._generate_excel(data, job_id, timestamp)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    async def _generate_csv(self, data: List[Dict], job_id: str, timestamp: str) -> str:
        """Generate CSV export with compression"""
        # Ensure exports directory exists
        os.makedirs("exports", exist_ok=True)
        file_path = f"exports/quiz_export_{timestamp}_{job_id}.csv.gz"
        
        df = pd.DataFrame(data)
        
        # Optimize column order
        if not df.empty:
            priority_cols = ['user_id', 'quiz_id', 'score', 'completed_at']
            other_cols = [col for col in df.columns if col not in priority_cols]
            df = df[priority_cols + other_cols]
        
        # Write compressed CSV
        with gzip.open(file_path, 'wt', encoding='utf-8') as f:
            df.to_csv(f, index=False, encoding='utf-8')
        
        return file_path
    
    async def _generate_json(self, data: List[Dict], job_id: str, timestamp: str) -> str:
        """Generate JSON export with compression"""
        # Ensure exports directory exists
        os.makedirs("exports", exist_ok=True)
        file_path = f"exports/quiz_export_{timestamp}_{job_id}.json.gz"
        
        export_data = {
            'metadata': {
                'export_date': datetime.utcnow().isoformat(),
                'total_records': len(data),
                'job_id': job_id
            },
            'data': data
        }
        
        with gzip.open(file_path, 'wt', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        return file_path
    
    async def _generate_xml(self, data: List[Dict], job_id: str, timestamp: str) -> str:
        """Generate XML export"""
        file_path = f"exports/quiz_export_{timestamp}_{job_id}.xml"
        
        root = ET.Element("quiz_export")
        metadata = ET.SubElement(root, "metadata")
        ET.SubElement(metadata, "export_date").text = datetime.utcnow().isoformat()
        ET.SubElement(metadata, "total_records").text = str(len(data))
        ET.SubElement(metadata, "job_id").text = job_id
        
        records = ET.SubElement(root, "records")
        for record in data:
            record_elem = ET.SubElement(records, "record")
            for key, value in record.items():
                elem = ET.SubElement(record_elem, key)
                elem.text = str(value) if value is not None else ""
        
        tree = ET.ElementTree(root)
        tree.write(file_path, encoding='utf-8', xml_declaration=True)
        
        return file_path
    
    async def _generate_pdf(self, data: List[Dict], job_id: str, timestamp: str) -> str:
        """Generate PDF report"""
        file_path = f"exports/quiz_export_{timestamp}_{job_id}.pdf"
        
        doc = SimpleDocTemplate(file_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title = Paragraph("Quiz Results Export Report", styles['Title'])
        story.append(title)
        
        # Summary statistics
        if data:
            df = pd.DataFrame(data)
            summary_data = [
                ['Total Records', len(data)],
                ['Average Score', f"{df['score'].mean():.2f}"],
                ['Max Score', f"{df['score'].max():.2f}"],
                ['Min Score', f"{df['score'].min():.2f}"],
                ['Export Date', datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')]
            ]
            
            summary_table = Table(summary_data)
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(summary_table)
        
        doc.build(story)
        return file_path
    
    async def _generate_excel(self, data: List[Dict], job_id: str, timestamp: str) -> str:
        """Generate Excel export with multiple sheets"""
        file_path = f"exports/quiz_export_{timestamp}_{job_id}.xlsx"
        
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            # Main data sheet
            df = pd.DataFrame(data)
            df.to_excel(writer, sheet_name='Quiz Results', index=False)
            
            # Summary sheet
            if not df.empty:
                summary_data = {
                    'Metric': ['Total Records', 'Average Score', 'Max Score', 'Min Score'],
                    'Value': [len(data), df['score'].mean(), df['score'].max(), df['score'].min()]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        return file_path
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get export job status"""
        job = self.db.query(ExportJob).filter(ExportJob.job_id == job_id).first()
        if not job:
            return None
        
        return {
            'job_id': job.job_id,
            'status': job.status.value,
            'progress': job.progress,
            'total_records': job.total_records,
            'processed_records': job.processed_records,
            'file_size': job.file_size,
            'created_at': job.created_at,
            'completed_at': job.completed_at,
            'error_message': job.error_message
        }
