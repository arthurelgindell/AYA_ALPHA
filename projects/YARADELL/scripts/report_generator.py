#!/usr/bin/env python3
"""
Yara ❤️ Dell YouTube Intelligence - Report Generator
Automated PDF and Markdown report creation with charts
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/Users/arthurdell/YARADELL/config/.env')


class ReportGenerator:
    """Generate comprehensive YouTube intelligence reports"""
    
    def __init__(self):
        self.db_conn = None
        self.report_dir = os.getenv('REPORT_OUTPUT_DIR', '/Users/arthurdell/YARADELL/reports')
        self.chart_dir = os.path.join(self.report_dir, 'charts')
        
        # Create directories
        os.makedirs(self.report_dir, exist_ok=True)
        os.makedirs(self.chart_dir, exist_ok=True)
        
    def connect_database(self):
        """Connect to aya_rag PostgreSQL database"""
        try:
            self.db_conn = psycopg2.connect(
                host=os.getenv('POSTGRES_HOST', 'localhost'),
                port=os.getenv('POSTGRES_PORT', '5432'),
                database=os.getenv('POSTGRES_DB', 'aya_rag'),
                user=os.getenv('POSTGRES_USER', 'postgres'),
                password=os.getenv('POSTGRES_PASSWORD')
            )
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def generate_demographic_chart(self, channel_id: str, days: int = 30) -> str:
        """Generate age distribution chart"""
        if not self.db_conn:
            self.connect_database()
        
        cursor = self.db_conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
        SELECT 
            snapshot_date,
            age_18_24_percent,
            age_25_34_percent,
            age_35_44_percent,
            age_45_54_percent
        FROM youtube_audience_demographics
        WHERE channel_id = %s 
            AND snapshot_date >= CURRENT_DATE - INTERVAL '%s days'
        ORDER BY snapshot_date ASC
        """
        
        cursor.execute(query, (channel_id, days))
        rows = cursor.fetchall()
        cursor.close()
        
        if not rows:
            return None
        
        # Extract data
        dates = [row['snapshot_date'] for row in rows]
        age_18_24 = [row['age_18_24_percent'] or 0 for row in rows]
        age_25_34 = [row['age_25_34_percent'] or 0 for row in rows]
        age_35_44 = [row['age_35_44_percent'] or 0 for row in rows]
        age_45_54 = [row['age_45_54_percent'] or 0 for row in rows]
        
        # Create chart
        plt.figure(figsize=(10, 6))
        plt.plot(dates, age_18_24, marker='o', label='18-24', linewidth=2)
        plt.plot(dates, age_25_34, marker='s', label='25-34', linewidth=2)
        plt.plot(dates, age_35_44, marker='^', label='35-44', linewidth=2)
        plt.plot(dates, age_45_54, marker='d', label='45-54', linewidth=2)
        
        plt.title('Age Distribution Trends - Yara ❤️ Dell', fontsize=14, fontweight='bold')
        plt.xlabel('Date')
        plt.ylabel('Percentage (%)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        chart_path = os.path.join(self.chart_dir, 'demographics_trend.png')
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def generate_engagement_chart(self, channel_id: str, days: int = 30) -> str:
        """Generate engagement rate chart"""
        if not self.db_conn:
            self.connect_database()
        
        cursor = self.db_conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
        SELECT 
            snapshot_date,
            engagement_rate,
            views_total,
            likes_total
        FROM youtube_audience_behavior
        WHERE channel_id = %s 
            AND snapshot_date >= CURRENT_DATE - INTERVAL '%s days'
        ORDER BY snapshot_date ASC
        """
        
        cursor.execute(query, (channel_id, days))
        rows = cursor.fetchall()
        cursor.close()
        
        if not rows:
            return None
        
        # Extract data
        dates = [row['snapshot_date'] for row in rows]
        engagement = [row['engagement_rate'] or 0 for row in rows]
        
        # Create chart
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(dates, engagement, marker='o', color='#FF0000', linewidth=2, markersize=8)
        ax.fill_between(dates, engagement, alpha=0.3, color='#FF0000')
        
        ax.set_title('Engagement Rate Trend - Yara ❤️ Dell', fontsize=14, fontweight='bold')
        ax.set_xlabel('Date')
        ax.set_ylabel('Engagement Rate (%)')
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        
        chart_path = os.path.join(self.chart_dir, 'engagement_trend.png')
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def generate_markdown_report(self, channel_id: str, insights: Dict[str, Any]) -> str:
        """Generate comprehensive Markdown report"""
        timestamp = datetime.now().strftime('%Y-%m-%d')
        
        report_content = f"""# Yara ❤️ Dell - YouTube Intelligence Report
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Channel ID**: {channel_id}  
**Analysis Period**: Last 7 days

---

## Executive Summary

{insights.get('summary', 'No summary available')}

---

## Key Findings

"""
        
        for i, finding in enumerate(insights.get('key_findings', []), 1):
            report_content += f"{i}. {finding}\n"
        
        report_content += "\n---\n\n## Actionable Recommendations\n\n"
        
        for i, rec in enumerate(insights.get('recommendations', []), 1):
            report_content += f"### {i}. {rec.get('action', 'N/A')}\n\n"
            report_content += f"**Reason**: {rec.get('reason', 'N/A')}\n\n"
            report_content += f"**Expected Impact**: {rec.get('expected_impact', 'N/A')}\n\n"
        
        report_content += f"""---

## Analysis Confidence

**Confidence Score**: {insights.get('confidence', 0):.1%}

---

## Charts and Visualizations

![Demographics Trend](charts/demographics_trend.png)

![Engagement Trend](charts/engagement_trend.png)

---

## Data Sources

- YouTube Data API v3
- YouTube Analytics API
- AI Analysis: LM Studio
- Database: aya_rag (PostgreSQL)

---

*This report was automatically generated by the Yara ❤️ Dell YouTube Intelligence System*
"""
        
        # Save report
        report_path = os.path.join(self.report_dir, f'youtube_report_{timestamp}.md')
        with open(report_path, 'w') as f:
            f.write(report_content)
        
        print(f"✅ Markdown report saved: {report_path}")
        return report_path
    
    def generate_pdf_report(self, channel_id: str, insights: Dict[str, Any], 
                           demo_chart: str = None, eng_chart: str = None) -> str:
        """Generate comprehensive PDF report"""
        timestamp = datetime.now().strftime('%Y-%m-%d')
        report_path = os.path.join(self.report_dir, f'youtube_report_{timestamp}.pdf')
        
        # Create PDF
        doc = SimpleDocTemplate(report_path, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#FF0000'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#333333'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Title
        story.append(Paragraph("Yara ❤️ Dell", title_style))
        story.append(Paragraph("YouTube Intelligence Report", styles['Heading2']))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Paragraph(f"Channel ID: {channel_id}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", heading_style))
        story.append(Paragraph(insights.get('summary', 'No summary available'), styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Key Findings
        story.append(Paragraph("Key Findings", heading_style))
        for i, finding in enumerate(insights.get('key_findings', []), 1):
            story.append(Paragraph(f"{i}. {finding}", styles['Normal']))
            story.append(Spacer(1, 6))
        story.append(Spacer(1, 20))
        
        # Recommendations
        story.append(Paragraph("Actionable Recommendations", heading_style))
        for i, rec in enumerate(insights.get('recommendations', []), 1):
            story.append(Paragraph(f"<b>{i}. {rec.get('action', 'N/A')}</b>", styles['Normal']))
            story.append(Spacer(1, 6))
            story.append(Paragraph(f"<b>Reason:</b> {rec.get('reason', 'N/A')}", styles['Normal']))
            story.append(Spacer(1, 6))
            story.append(Paragraph(f"<b>Expected Impact:</b> {rec.get('expected_impact', 'N/A')}", styles['Normal']))
            story.append(Spacer(1, 12))
        
        # Charts
        if demo_chart and os.path.exists(demo_chart):
            story.append(PageBreak())
            story.append(Paragraph("Demographics Trend", heading_style))
            story.append(Image(demo_chart, width=6*inch, height=3.6*inch))
            story.append(Spacer(1, 20))
        
        if eng_chart and os.path.exists(eng_chart):
            story.append(Paragraph("Engagement Trend", heading_style))
            story.append(Image(eng_chart, width=6*inch, height=3.6*inch))
        
        # Build PDF
        doc.build(story)
        print(f"✅ PDF report saved: {report_path}")
        return report_path
    
    def generate_complete_report(self, channel_id: str) -> Dict[str, str]:
        """Generate all report formats"""
        print("=" * 60)
        print("Yara ❤️ Dell - Report Generation")
        print("=" * 60)
        
        # Connect to database
        if not self.connect_database():
            return {"error": "Database connection failed"}
        
        # Get latest insights
        cursor = self.db_conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT summary, key_findings, recommendations, confidence_score
            FROM youtube_insights_log
            WHERE channel_id = %s
            ORDER BY insight_date DESC
            LIMIT 1
        """, (channel_id,))
        
        row = cursor.fetchone()
        cursor.close()
        
        if not row:
            print("⚠️  No insights found in database")
            insights = {
                'summary': 'No analysis data available yet',
                'key_findings': [],
                'recommendations': [],
                'confidence': 0.0
            }
        else:
            insights = {
                'summary': row['summary'],
                'key_findings': json.loads(row['key_findings']),
                'recommendations': json.loads(row['recommendations']),
                'confidence': float(row['confidence_score'])
            }
        
        # Generate charts
        print("\n📊 Generating charts...")
        demo_chart = self.generate_demographic_chart(channel_id, days=30)
        eng_chart = self.generate_engagement_chart(channel_id, days=30)
        
        print(f"  Demographics: {'✅' if demo_chart else '❌'}")
        print(f"  Engagement: {'✅' if eng_chart else '❌'}")
        
        # Generate reports
        print("\n📄 Generating reports...")
        md_report = self.generate_markdown_report(channel_id, insights)
        pdf_report = self.generate_pdf_report(channel_id, insights, demo_chart, eng_chart)
        
        return {
            'markdown': md_report,
            'pdf': pdf_report,
            'charts': {
                'demographics': demo_chart,
                'engagement': eng_chart
            }
        }
    
    def close(self):
        """Close database connection"""
        if self.db_conn:
            self.db_conn.close()


def main():
    """Test report generation"""
    generator = ReportGenerator()
    
    channel_id = os.getenv('YOUTUBE_CHANNEL_ID')
    if not channel_id:
        print("❌ YOUTUBE_CHANNEL_ID not configured in .env")
        return
    
    reports = generator.generate_complete_report(channel_id)
    
    print("\n" + "=" * 60)
    print("REPORTS GENERATED")
    print("=" * 60)
    print(json.dumps(reports, indent=2))
    
    generator.close()


if __name__ == "__main__":
    main()

