from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
from datetime import datetime
from typing import Dict, List


class PDFReportGenerator:
    """
    Generates PDF reports for security analysis results
    """
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Risk level styles
        self.styles.add(ParagraphStyle(
            name='RiskCritical',
            parent=self.styles['Normal'],
            fontSize=16,
            textColor=colors.HexColor('#dc3545'),
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='RiskHigh',
            parent=self.styles['Normal'],
            fontSize=16,
            textColor=colors.HexColor('#fd7e14'),
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='RiskMedium',
            parent=self.styles['Normal'],
            fontSize=16,
            textColor=colors.HexColor('#ffc107'),
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='RiskLow',
            parent=self.styles['Normal'],
            fontSize=16,
            textColor=colors.HexColor('#28a745'),
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        ))
        
        # Section heading
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            fontName='Helvetica-Bold'
        ))
        
        # Insight item
        self.styles.add(ParagraphStyle(
            name='InsightItem',
            parent=self.styles['Normal'],
            fontSize=10,
            leftIndent=20,
            spaceAfter=8,
            bulletIndent=10
        ))
    
    def generate_report(self, analysis_data: Dict) -> BytesIO:
        """
        Generate PDF report from analysis data
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, 
                               rightMargin=72, leftMargin=72,
                               topMargin=72, bottomMargin=18)
        
        # Build the document content
        story = []
        
        # Title
        story.append(Paragraph("Security Analysis Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.2*inch))
        
        # Generated date
        date_text = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        story.append(Paragraph(date_text, self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", self.styles['SectionHeading']))
        summary_text = analysis_data.get('summary', 'No summary available')
        story.append(Paragraph(summary_text, self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Risk Assessment
        risk_level = analysis_data.get('risk_level', 'unknown').upper()
        risk_score = analysis_data.get('risk_score', 0)
        
        story.append(Paragraph("Risk Assessment", self.styles['SectionHeading']))
        
        # Risk score and level in a table
        risk_data = [
            ['Risk Score', str(risk_score)],
            ['Risk Level', risk_level]
        ]
        risk_table = Table(risk_data, colWidths=[2*inch, 3*inch])
        
        # Color based on risk level
        risk_color = self._get_risk_color(risk_level)
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('TEXTCOLOR', (1, 1), (1, 1), risk_color),
            ('FONTNAME', (1, 1), (1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (1, 1), (1, 1), 14),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
            ('PADDING', (0, 0), (-1, -1), 12),
        ]))
        story.append(risk_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Statistics
        statistics = analysis_data.get('statistics', {})
        story.append(Paragraph("Findings Breakdown", self.styles['SectionHeading']))
        
        stats_data = [
            ['Severity', 'Count'],
            ['Critical', str(statistics.get('critical', 0))],
            ['High', str(statistics.get('high', 0))],
            ['Medium', str(statistics.get('medium', 0))],
            ['Low', str(statistics.get('low', 0))],
            ['Total', str(statistics.get('total_findings', 0))]
        ]
        
        stats_table = Table(stats_data, colWidths=[2*inch, 3*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#343a40')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
            ('PADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(stats_table)
        story.append(Spacer(1, 0.3*inch))
        
        # AI Insights
        insights = analysis_data.get('insights', [])
        if insights:
            story.append(Paragraph("Key Security Insights", self.styles['SectionHeading']))
            for idx, insight in enumerate(insights, 1):
                bullet_text = f"• {insight}"
                story.append(Paragraph(bullet_text, self.styles['InsightItem']))
            story.append(Spacer(1, 0.3*inch))
        
        # Detailed Findings
        findings = analysis_data.get('findings', [])
        if findings:
            story.append(Spacer(1, 0.4*inch))
            story.append(Paragraph("Detailed Findings", self.styles['SectionHeading']))
            
            # Group findings by risk level
            findings_by_risk = {
                'critical': [],
                'high': [],
                'medium': [],
                'low': []
            }
            
            for finding in findings:
                risk = finding.get('risk', 'low')
                findings_by_risk[risk].append(finding)
            
            # Display findings by severity
            for risk_level in ['critical', 'high', 'medium', 'low']:
                risk_findings = findings_by_risk[risk_level]
                if risk_findings:
                    story.append(Paragraph(
                        f"{risk_level.capitalize()} Severity Findings ({len(risk_findings)})",
                        self.styles['Heading3']
                    ))
                    
                    for finding in risk_findings[:10]:  # Limit to 10 per category
                        finding_type = finding.get('type', 'Unknown')
                        line = finding.get('line', 'N/A')
                        description = finding.get('description', 'No description')
                        
                        finding_text = f"<b>Type:</b> {finding_type} | <b>Line:</b> {line}<br/>{description}"
                        story.append(Paragraph(finding_text, self.styles['Normal']))
                        story.append(Spacer(1, 0.15*inch))
                    
                    if len(risk_findings) > 10:
                        story.append(Paragraph(
                            f"<i>... and {len(risk_findings) - 10} more {risk_level} findings</i>",
                            self.styles['Normal']
                        ))
                        story.append(Spacer(1, 0.2*inch))
        
        # Recommendations - add space separator if findings existed, otherwise start on same page
        if findings:
            story.append(Spacer(1, 0.5*inch))
        
        story.append(Paragraph("Recommendations", self.styles['SectionHeading']))
        
        recommendations = self._generate_recommendations(analysis_data)
        for rec in recommendations:
            story.append(Paragraph(f"• {rec}", self.styles['InsightItem']))
        
        story.append(Spacer(1, 0.5*inch))
        
        # Footer
        footer_text = "This report was generated by AI Secure Data Intelligence Platform"
        story.append(Paragraph(footer_text, self.styles['Normal']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def _get_risk_color(self, risk_level: str):
        """Get color for risk level"""
        colors_map = {
            'CRITICAL': colors.HexColor('#dc3545'),
            'HIGH': colors.HexColor('#fd7e14'),
            'MEDIUM': colors.HexColor('#ffc107'),
            'LOW': colors.HexColor('#28a745'),
        }
        return colors_map.get(risk_level, colors.black)
    
    def _generate_recommendations(self, analysis_data: Dict) -> List[str]:
        """Generate security recommendations based on findings"""
        recommendations = []
        
        # Check for critical findings
        statistics = analysis_data.get('statistics', {})
        findings = analysis_data.get('findings', [])
        
        if statistics.get('critical', 0) > 0:
            recommendations.append(
                "URGENT: Immediately rotate all exposed credentials (passwords, API keys, secrets)"
            )
            recommendations.append(
                "Review access logs and CloudTrail/audit logs for unauthorized access"
            )
        
        if statistics.get('high', 0) > 0:
            recommendations.append(
                "Implement secrets management solution (e.g., HashiCorp Vault, AWS Secrets Manager)"
            )
        
        # Check for specific finding types
        finding_types = [f.get('type', '') for f in findings]
        
        if 'credit_card' in finding_types:
            recommendations.append(
                "Ensure PCI DSS compliance - encrypt credit card data and limit storage"
            )
        
        if 'email' in finding_types or 'personal_info' in finding_types:
            recommendations.append(
                "Review GDPR/privacy compliance - implement data encryption and access controls"
            )
        
        if 'stack_trace' in finding_types or 'debug_mode' in finding_types:
            recommendations.append(
                "Disable debug mode in production and implement proper error handling"
            )
        
        # General recommendations
        recommendations.append(
            "Implement centralized logging and monitoring with sensitive data filtering"
        )
        recommendations.append(
            "Conduct regular security audits and staff security awareness training"
        )
        recommendations.append(
            "Use environment variables and secure vaults for sensitive configuration"
        )
        
        return recommendations
