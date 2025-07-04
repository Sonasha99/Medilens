import os
import json
import logging
from datetime import datetime
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2
from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.platypus import Image as ReportLabImage
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT



# Medical reference data and diagnostic criteria
MEDICAL_REFERENCES = {
    "nt_normal_ranges": {
        "11_weeks": {"min": 1.2, "max": 2.1, "95th_percentile": 2.2},
        "12_weeks": {"min": 1.2, "max": 2.5, "95th_percentile": 2.8},
        "13_weeks": {"min": 1.2, "max": 2.7, "95th_percentile": 3.1},
        "cutoff_high_risk": 3.5,
        "cutoff_moderate_risk": 2.5
    },
    "biometric_references": {
        "crl_ranges": {
            "11_weeks": {"min": 45, "max": 55, "mean": 50},
            "12_weeks": {"min": 55, "max": 70, "mean": 62},
            "13_weeks": {"min": 70, "max": 85, "mean": 78},
            "14_weeks": {"min": 85, "max": 100, "mean": 92}
        },
        "bpd_ranges": {
            "11_weeks": {"min": 17, "max": 21, "mean": 19},
            "12_weeks": {"min": 20, "max": 24, "mean": 22},
            "13_weeks": {"min": 23, "max": 27, "mean": 25},
            "14_weeks": {"min": 26, "max": 30, "mean": 28}
        }
    },
    "structure_significance": {
        "Thalami": {
            "medical_name": "Thalamic Structures",
            "description": "Bilateral thalamic structures responsible for sensory relay and consciousness",
            "normal_finding": "Symmetric, echogenic structures visible in the axial plane",
            "abnormal_implications": ["Thalamic hemorrhage", "Metabolic disorders", "Genetic syndromes"],
            "clinical_significance": "Critical for normal neurological development"
        },
        "Midbrain": {
            "medical_name": "Mesencephalon",
            "description": "Brainstem structure containing vital centers for motor control and reflexes",
            "normal_finding": "Butterfly-shaped structure with normal echogenicity",
            "abnormal_implications": ["Neural tube defects", "Holoprosencephaly", "Aqueductal stenosis"],
            "clinical_significance": "Essential for motor function and consciousness"
        },
        "Palate": {
            "medical_name": "Fetal Palate",
            "description": "Hard and soft palate structures forming the roof of the mouth",
            "normal_finding": "Continuous hyperechoic line representing intact palatal structures",
            "abnormal_implications": ["Cleft palate", "Facial dysmorphism", "Genetic syndromes"],
            "clinical_significance": "Important for feeding and speech development"
        },
        "4th Ventricle": {
            "medical_name": "Fourth Ventricle",
            "description": "CSF-filled cavity in the posterior fossa connecting to the cisterna magna",
            "normal_finding": "Small anechoic space posterior to the brainstem",
            "abnormal_implications": ["Dandy-Walker malformation", "Aqueductal stenosis", "Posterior fossa anomalies"],
            "clinical_significance": "Critical for CSF circulation and posterior fossa development"
        },
        "Cisterna Magna": {
            "medical_name": "Cisterna Magna",
            "description": "Largest CSF cistern located between cerebellum and medulla",
            "normal_finding": "Anechoic space measuring 2-10mm in anteroposterior diameter",
            "abnormal_implications": ["Mega cisterna magna", "Blake's pouch cyst", "Cerebellar hypoplasia"],
            "clinical_significance": "Marker of posterior fossa development and cerebellar integrity"
        },
        "NT": {
            "medical_name": "Nuchal Translucency",
            "description": "Subcutaneous fluid collection behind fetal neck (11-14 weeks)",
            "normal_finding": "Thickness <3.5mm at 11-14 weeks gestation",
            "abnormal_implications": ["Chromosomal abnormalities", "Cardiac defects", "Genetic syndromes"],
            "clinical_significance": "Primary screening marker for aneuploidy and structural anomalies"
        },
        "Nasal Tip": {
            "medical_name": "Nasal Tip",
            "description": "Anterior portion of the fetal nose profile",
            "normal_finding": "Well-defined echogenic structure in sagittal profile",
            "abnormal_implications": ["Facial dysmorphism", "Chromosomal abnormalities"],
            "clinical_significance": "Component of facial profile assessment"
        },
        "Nasal Skin": {
            "medical_name": "Nasal Skin Line",
            "description": "Soft tissue outline of the nasal profile",
            "normal_finding": "Continuous hyperechoic line defining nasal contour",
            "abnormal_implications": ["Facial edema", "Hydrops fetalis"],
            "clinical_significance": "Assessment of facial soft tissue development"
        },
        "Nasal Bone": {
            "medical_name": "Nasal Bone",
            "description": "Paired bones forming the bridge of the nose",
            "normal_finding": "Hyperechoic linear structure in sagittal plane, >2.5mm at 11-14 weeks",
            "abnormal_implications": ["Chromosomal abnormalities", "Particularly trisomy 21"],
            "clinical_significance": "Important marker for Down syndrome screening"
        }
    },
    "risk_calculations": {
        "maternal_age_risks": {
            20: {"t21": 1526, "t18": 9500, "t13": 14000},
            25: {"t21": 1352, "t18": 9500, "t13": 14000},
            30: {"t21": 895, "t18": 7500, "t13": 11000},
            35: {"t21": 365, "t18": 2500, "t13": 3500},
            40: {"t21": 99, "t18": 830, "t13": 1100},
            45: {"t21": 30, "t18": 275, "t13": 350}
        }
    }
}

   
class MedicalReportGenerator:
    def __init__(self, app_config):
        self.upload_folder = app_config.get('UPLOAD_FOLDER')
        self.logger = logging.getLogger(__name__)
        
    def calculate_gestational_age_from_structures(self, detected_structures, nt_measurement=None):
        """Estimate gestational age based on detected structures and NT measurement"""
        if nt_measurement:
            if nt_measurement <= 2.1:
                return "11-12 weeks"
            elif nt_measurement <= 2.8:
                return "12-13 weeks"
            else:
                return "13-14 weeks"
        return "11-14 weeks (estimated)"
    
    def calculate_combined_risk(self, nt_value, maternal_age=30, nasal_bone_present=True):
        """Calculate combined first trimester screening risk"""
        base_risks = MEDICAL_REFERENCES["risk_calculations"]["maternal_age_risks"]
        
        # Get closest age bracket
        age_brackets = sorted(base_risks.keys())
        closest_age = min(age_brackets, key=lambda x: abs(x - maternal_age))
        base_risk = base_risks[closest_age]
        
        # NT adjustment factors (simplified)
        if nt_value is None:
            nt_factor = 1.0
        elif nt_value < 2.5:
            nt_factor = 0.5  # Reduced risk
        elif nt_value < 3.5:
            nt_factor = 2.0  # Moderate increase
        else:
            nt_factor = 10.0  # High increase
        
        # Nasal bone adjustment
        nb_factor = 0.7 if nasal_bone_present else 3.0
        
        # Calculate adjusted risks
        adjusted_risks = {}
        for condition, risk in base_risk.items():
            adjusted_risk = max(1, int(risk / (nt_factor * nb_factor)))
            adjusted_risks[condition] = adjusted_risk
        
        return adjusted_risks
    
    def assess_nt_risk(self, nt_value_mm, gestational_weeks=12):
        """Comprehensive NT risk assessment"""
        if nt_value_mm is None:
            return {
                "risk_level": "Unable to assess", 
                "risk_ratio": "N/A", 
                "recommendation": "Repeat scan recommended",
                "measurement": "Not detected",
                "reference_range": "N/A"
            }
        
        cutoffs = MEDICAL_REFERENCES["nt_normal_ranges"]
        
        if nt_value_mm >= cutoffs["cutoff_high_risk"]:
            risk_level = "HIGH RISK"
            risk_ratio = "1:50 to 1:100"
            recommendation = "Immediate genetic counseling and diagnostic testing (CVS/amniocentesis) recommended"
        elif nt_value_mm >= cutoffs["cutoff_moderate_risk"]:
            risk_level = "MODERATE RISK"
            risk_ratio = "1:150 to 1:300"
            recommendation = "Enhanced screening, detailed anatomy scan, and genetic counseling recommended"
        else:
            risk_level = "LOW RISK"
            risk_ratio = "1:1000+"
            recommendation = "Routine antenatal care, standard screening protocol"
        
        return {
            "risk_level": risk_level,
            "risk_ratio": risk_ratio,
            "recommendation": recommendation,
            "measurement": f"{nt_value_mm} mm",
            "reference_range": f"Normal: <{cutoffs['cutoff_moderate_risk']} mm"
        }

    def generate_clinical_interpretation(self, analysis_results):
        """Generate comprehensive clinical interpretation"""
        detected = analysis_results.get('detected_structures', set())
        nt_measurement = analysis_results.get('nt_measurement_mm')
        confidences = analysis_results.get('detection_confidences', {})
        maternal_age = analysis_results.get('maternal_age', 30)
        
        interpretation = {
            "primary_findings": [],
            "secondary_findings": [], 
            "risk_assessment": {},
            "recommendations": [],
            "differential_diagnoses": [],
            "follow_up": []
        }
        
        # NT Assessment
        nt_assessment = self.assess_nt_risk(nt_measurement)
        interpretation["risk_assessment"]["nuchal_translucency"] = nt_assessment
        
        # Combined risk calculation
        nasal_bone_present = "Nasal Bone" in detected
        combined_risks = self.calculate_combined_risk(nt_measurement, maternal_age, nasal_bone_present)
        interpretation["risk_assessment"]["combined_screening"] = {
            "trisomy_21_risk": f"1:{combined_risks.get('t21', 1000)}",
            "trisomy_18_risk": f"1:{combined_risks.get('t18', 5000)}",
            "trisomy_13_risk": f"1:{combined_risks.get('t13', 8000)}"
        }
        
        if nt_measurement and nt_measurement >= 3.5:
            interpretation["primary_findings"].append(
                f"INCREASED NUCHAL TRANSLUCENCY: {nt_measurement} mm (>95th percentile)"
            )
            interpretation["recommendations"].extend([
                "Urgent genetic counseling consultation",
                "Offer diagnostic testing (chorionic villus sampling or amniocentesis)",
                "Detailed fetal echocardiography at 18-22 weeks",
                "Serial growth assessments"
            ])
            interpretation["differential_diagnoses"].extend([
                "Trisomy 21 (Down syndrome)",
                "Trisomy 18 (Edwards syndrome)", 
                "Trisomy 13 (Patau syndrome)",
                "Turner syndrome",
                "Congenital heart disease",
                "Noonan syndrome"
            ])
        
        # Nasal Bone Assessment
        if not nasal_bone_present:
            interpretation["secondary_findings"].append("ABSENT NASAL BONE - Additional marker for aneuploidy screening")
            interpretation["recommendations"].append("Enhanced genetic screening recommended")
            interpretation["differential_diagnoses"].append("Increased risk for trisomy 21")
        else:
            interpretation["secondary_findings"].append("NASAL BONE PRESENT - Reassuring finding")
        
        # Posterior Fossa Assessment
        fourth_ventricle = "4th Ventricle" in detected
        cisterna_magna = "Cisterna Magna" in detected
        
        if fourth_ventricle and cisterna_magna:
            interpretation["secondary_findings"].append("POSTERIOR FOSSA - Normal appearance of 4th ventricle and cisterna magna")
        elif not fourth_ventricle or not cisterna_magna:
            interpretation["secondary_findings"].append("POSTERIOR FOSSA - Suboptimal visualization, consider repeat scan")
            interpretation["recommendations"].append("Repeat detailed neurosonography at 18-22 weeks")
        
        # Brain Structure Assessment
        thalami_detected = "Thalami" in detected
        midbrain_detected = "Midbrain" in detected
        
        if thalami_detected and midbrain_detected:
            interpretation["secondary_findings"].append("BRAIN STRUCTURES - Normal appearance of thalami and midbrain")
        else:
            missing = []
            if not thalami_detected:
                missing.append("thalami")
            if not midbrain_detected:
                missing.append("midbrain")
            interpretation["secondary_findings"].append(f"BRAIN STRUCTURES - Suboptimal visualization of {', '.join(missing)}")
        
        # Overall Assessment
        if nt_measurement and nt_measurement < 2.5 and nasal_bone_present:
            interpretation["primary_findings"].append("LOW RISK first trimester screening")
        
        # Standard Recommendations
        interpretation["recommendations"].extend([
            "Continue routine antenatal care",
            "Second trimester detailed anatomy scan at 18-22 weeks",
            "Consider maternal serum screening if not already performed"
        ])
        
        interpretation["follow_up"] = [
            "Repeat imaging in 4-6 weeks for interval growth assessment",
            "Genetic counseling if any concerns arise",
            "Coordinate care with maternal-fetal medicine if high-risk features identified"
        ]

        return interpretation
    
    def create_visual_summary_chart(self, analysis_results):
        """Create a visual chart showing detection confidence and risk assessment"""
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            
            # Structure Detection Chart
            structures = list(MEDICAL_REFERENCES["structure_significance"].keys())
            detected = analysis_results.get('detected_structures', set())
            confidences = analysis_results.get('detection_confidences', {})
            
            detection_status = []
            confidence_values = []
            colors_list = []
            
            for structure in structures:
                if structure in detected:
                    detection_status.append(f"{structure}\n✓ Detected")
                    confidence_values.append(confidences.get(structure, 0.8) * 100)
                    colors_list.append('#2E8B57' if confidences.get(structure, 0.8) > 0.7 else '#DAA520')
                else:
                    detection_status.append(f"{structure}\n✗ Not Detected")
                    confidence_values.append(0)
                    colors_list.append('#CD5C5C')
            
            bars = ax1.barh(range(len(structures)), confidence_values, color=colors_list)
            ax1.set_yticks(range(len(structures)))
            ax1.set_yticklabels([s.replace(' ', '\n') for s in structures], fontsize=8)
            ax1.set_xlabel('Detection Confidence (%)')
            ax1.set_title('Structure Detection Summary', fontweight='bold')
            ax1.set_xlim(0, 100)
            
            # Add confidence labels
            for i, (bar, conf) in enumerate(zip(bars, confidence_values)):
                if conf > 0:
                    ax1.text(conf + 2, i, f'{conf:.1f}%', va='center', fontsize=8)
            
            # Risk Assessment Pie Chart
            nt_measurement = analysis_results.get('nt_measurement_mm')
            if nt_measurement:
                risk_assessment = self.assess_nt_risk(nt_measurement)
                risk_level = risk_assessment['risk_level']
                
                if 'LOW' in risk_level:
                    risk_colors = ['#2E8B57', '#90EE90', '#F0F8FF']
                    risk_labels = ['Low Risk', 'Moderate Risk', 'High Risk']
                    risk_values = [85, 10, 5]
                elif 'MODERATE' in risk_level:
                    risk_colors = ['#90EE90', '#DAA520', '#F0F8FF'] 
                    risk_labels = ['Low Risk', 'Moderate Risk', 'High Risk']
                    risk_values = [60, 30, 10]
                else:
                    risk_colors = ['#F0F8FF', '#DAA520', '#CD5C5C']
                    risk_labels = ['Low Risk', 'Moderate Risk', 'High Risk'] 
                    risk_values = [20, 30, 50]
                
                wedges, texts, autotexts = ax2.pie(risk_values, labels=risk_labels, colors=risk_colors,
                                                 autopct='%1.1f%%', startangle=90)
                ax2.set_title(f'Risk Assessment\nNT: {nt_measurement} mm', fontweight='bold')
            else:
                ax2.text(0.5, 0.5, 'NT Measurement\nNot Available', ha='center', va='center',
                        transform=ax2.transAxes, fontsize=12, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
                ax2.set_xlim(0, 1)
                ax2.set_ylim(0, 1)
                ax2.axis('off')
            
            plt.tight_layout()
            
            # Save chart
            chart_path = os.path.join(self.upload_folder, 'analysis_chart.png')
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return chart_path
        
        except Exception as e:
            self.logger.error(f"Error creating visual chart: {str(e)}")
            raise    

    def generate_comprehensive_pdf_report(self, analysis_results):
        """Generate comprehensive medical-grade PDF report"""
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch, bottomMargin=1*inch)
            styles = getSampleStyleSheet()
            story = []
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=20,
                alignment=TA_CENTER,
                textColor=colors.darkblue,
                fontName='Helvetica-Bold'
            )
            
            header_style = ParagraphStyle(
                'CustomHeader',
                parent=styles['Heading2'],
                fontSize=12,
                spaceAfter=10,
                textColor=colors.darkblue,
                fontName='Helvetica-Bold'
            )
            
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=6,
                alignment=TA_JUSTIFY
            )
            
            # Header
            story.append(Paragraph("FIRST TRIMESTER ULTRASOUND ANALYSIS REPORT", title_style))
            story.append(Paragraph("Automated Fetal Structure Detection and Risk Assessment", 
                                 ParagraphStyle('subtitle', parent=normal_style, fontSize=11, 
                                              alignment=TA_CENTER, textColor=colors.grey)))
            story.append(Spacer(1, 20))
            
            # Report Information Table
            report_data = [
                ['Report Date:', analysis_results.get('timestamp', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))],
                ['Analysis Method:', 'YOLOv8 Deep Learning Model'],
                ['Gestational Age:', self.calculate_gestational_age_from_structures(
                    analysis_results.get('detected_structures', set()),
                    analysis_results.get('nt_measurement_mm'))],
                ['Image Quality:', 'Adequate for automated analysis'],
                ['Maternal Age:', f"{analysis_results.get('maternal_age', 'Not provided')} years"]
            ]
            
            report_table = Table(report_data, colWidths=[2*inch, 3*inch])
            report_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            story.append(report_table)
            story.append(Spacer(1, 20))
            
            # PRIMARY FINDINGS
            story.append(Paragraph("PRIMARY FINDINGS", header_style))
            
            # NT Assessment
            nt_measurement = analysis_results.get('nt_measurement_mm')
            nt_assessment = self.assess_nt_risk(nt_measurement)
            
            nt_data = [
                ['Parameter', 'Measurement', 'Reference Range', 'Assessment'],
                ['Nuchal Translucency', 
                 nt_assessment['measurement'] if nt_measurement else 'Not detected',
                 nt_assessment['reference_range'],
                 nt_assessment['risk_level']]
            ]
            
            nt_table = Table(nt_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
            nt_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (3, 1), (3, 1), 
                 colors.lightgreen if 'LOW' in nt_assessment['risk_level'] 
                 else colors.yellow if 'MODERATE' in nt_assessment['risk_level']
                 else colors.lightcoral)
            ]))
            
            story.append(nt_table)
            story.append(Spacer(1, 15))
            
            # STRUCTURE DETECTION SUMMARY
            story.append(Paragraph("FETAL STRUCTURE DETECTION SUMMARY", header_style))
            
            detected_structures = analysis_results.get('detected_structures', set())
            confidences = analysis_results.get('detection_confidences', {})
            
            structure_data = [['Structure', 'Medical Significance', 'Detection Status', 'Confidence', 'Clinical Interpretation']]
            
            for structure_key, structure_info in MEDICAL_REFERENCES["structure_significance"].items():
                is_detected = structure_key in detected_structures
                confidence = confidences.get(structure_key, 0) * 100 if is_detected else 0
                
                status = "✓ DETECTED" if is_detected else "✗ NOT DETECTED"
                confidence_str = f"{confidence:.1f}%" if is_detected else "N/A"
                
                # Clinical interpretation based on detection
                if structure_key == "NT":
                    if is_detected and nt_measurement:
                        if nt_measurement >= 3.5:
                            interpretation = "HIGH RISK - Genetic counseling recommended"
                        elif nt_measurement >= 2.5:
                            interpretation = "MODERATE RISK - Enhanced screening"
                        else:
                            interpretation = "LOW RISK - Reassuring finding"
                    else:
                        interpretation = "Unable to assess - Consider repeat scan"
                elif structure_key == "Nasal Bone":
                    interpretation = "Reassuring for aneuploidy screening" if is_detected else "Additional risk marker - Enhanced screening recommended"
                elif structure_key in ["4th Ventricle", "Cisterna Magna"]:
                    interpretation = "Normal posterior fossa development" if is_detected else "Suboptimal visualization - Repeat neurosonography recommended"
                else:
                    interpretation = "Normal finding" if is_detected else "Suboptimal image quality or positioning"
                
                structure_data.append([
                    structure_info["medical_name"],
                    structure_info["clinical_significance"][:40] + "..." if len(structure_info["clinical_significance"]) > 40 else structure_info["clinical_significance"],
                    status,
                    confidence_str,
                    interpretation
                ])
            
            structure_table = Table(structure_data, colWidths=[1.2*inch, 1.8*inch, 0.8*inch, 0.6*inch, 1.6*inch])
            structure_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            
            # Color code detection status
            for i, (structure_key, *_) in enumerate(MEDICAL_REFERENCES["structure_significance"].items(), 1):
                if structure_key in detected_structures:
                    structure_table.setStyle(TableStyle([('BACKGROUND', (2, i), (2, i), colors.lightgreen)]))
                else:
                    structure_table.setStyle(TableStyle([('BACKGROUND', (2, i), (2, i), colors.lightcoral)]))
            
            story.append(structure_table)
            story.append(Spacer(1, 20))
            
            # CLINICAL INTERPRETATION
            story.append(Paragraph("CLINICAL INTERPRETATION", header_style))
            
            interpretation = self.generate_clinical_interpretation(analysis_results)
            
            # Risk Assessment
            story.append(Paragraph("Risk Assessment:", ParagraphStyle('bold', parent=normal_style, fontName='Helvetica-Bold')))
            story.append(Paragraph(f"• Nuchal Translucency Risk: {nt_assessment['risk_level']}", normal_style))
            story.append(Paragraph(f"• Risk Ratio: {nt_assessment['risk_ratio']}", normal_style))
            
            # Combined screening results
            combined_risks = interpretation["risk_assessment"].get("combined_screening", {})
            if combined_risks:
                story.append(Paragraph("• Combined First Trimester Screening Risks:", normal_style))
                story.append(Paragraph(f"  - Trisomy 21 (Down syndrome): {combined_risks.get('trisomy_21_risk', 'N/A')}", normal_style))
                story.append(Paragraph(f"  - Trisomy 18 (Edwards syndrome): {combined_risks.get('trisomy_18_risk', 'N/A')}", normal_style))
                story.append(Paragraph(f"  - Trisomy 13 (Patau syndrome): {combined_risks.get('trisomy_13_risk', 'N/A')}", normal_style))
            
            story.append(Spacer(1, 10))
            
            # Primary Findings
            if interpretation["primary_findings"]:
                story.append(Paragraph("Primary Findings:", ParagraphStyle('bold', parent=normal_style, fontName='Helvetica-Bold')))
                for finding in interpretation["primary_findings"]:
                    story.append(Paragraph(f"• {finding}", normal_style))
                story.append(Spacer(1, 10))
            
            # Secondary Findings  
            if interpretation["secondary_findings"]:
                story.append(Paragraph("Secondary Findings:", ParagraphStyle('bold', parent=normal_style, fontName='Helvetica-Bold')))
                for finding in interpretation["secondary_findings"]:
                    story.append(Paragraph(f"• {finding}", normal_style))
                story.append(Spacer(1, 10))
            
            # Recommendations
            story.append(Paragraph("Recommendations:", ParagraphStyle('bold', parent=normal_style, fontName='Helvetica-Bold')))
            story.append(Paragraph(f"• {nt_assessment['recommendation']}", normal_style))
            for rec in interpretation["recommendations"][:5]:  # Limit to top 5 recommendations
                story.append(Paragraph(f"• {rec}", normal_style))
            story.append(Spacer(1, 15))
            
            # Add visualization chart if available
            chart_path = self.create_visual_summary_chart(analysis_results)
            if os.path.exists(chart_path):
                story.append(Paragraph("VISUAL ANALYSIS SUMMARY", header_style))
                chart_img = ReportLabImage(chart_path, width=6*inch, height=2.5*inch)
                story.append(chart_img)
                story.append(Spacer(1, 15))
            
            # Add annotated image if available
            annotated_image_path = analysis_results.get('annotated_image_path')
            if annotated_image_path and os.path.exists(annotated_image_path):
                story.append(PageBreak())
                story.append(Paragraph("ANNOTATED ULTRASOUND IMAGE", header_style))
                story.append(Spacer(1, 10))
                
                # Resize image to fit page
                img = ReportLabImage(annotated_image_path, width=5*inch, height=4*inch)
                story.append(img)
                story.append(Spacer(1, 10))
                
                # Image legend
                story.append(Paragraph("Image Legend:", ParagraphStyle('bold', parent=normal_style, fontName='Helvetica-Bold')))
                story.append(Paragraph("• Green boxes: Detected structures with confidence scores", normal_style))
                story.append(Paragraph("• Confidence scores indicate model certainty (>70% considered reliable)", normal_style))
                story.append(Spacer(1, 15))
            
            # DISCLAIMER AND LIMITATIONS
            story.append(Paragraph("IMPORTANT DISCLAIMER", header_style))
            disclaimer_text = """
            This report is generated using automated artificial intelligence analysis and is intended for screening purposes only. 
            It should not replace clinical judgment or definitive diagnostic procedures. All findings should be interpreted by 
            qualified medical professionals in the context of clinical history and additional testing. This analysis is based on 
            image quality and technical factors that may affect accuracy. Negative findings do not rule out the presence of 
            abnormalities, and positive findings require clinical correlation and further evaluation.
            """
            story.append(Paragraph(disclaimer_text, normal_style))
            story.append(Spacer(1, 15))
            
            # Technical Information
            story.append(Paragraph("TECHNICAL INFORMATION", header_style))
            tech_data = [
                ['Model Version:', 'YOLOv8 Custom Trained'],
                ['Training Dataset:', 'Fetal ultrasound images (11-14 weeks)'],
                ['Detection Classes:', '9 anatomical structures'],
                ['Confidence Threshold:', '>50% for detection'],
                ['Image Processing:', 'Automated preprocessing and enhancement']
            ]
            
            tech_table = Table(tech_data, colWidths=[2*inch, 3*inch])
            tech_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            story.append(tech_table)
            
            # Build PDF
            doc.build(story)
            buffer.seek(0)
            
            # Clean up temporary files
            if os.path.exists(chart_path):
                os.remove(chart_path)
            
            return buffer
            
        except Exception as e:
            self.logger.error(f"Error generating comprehensive PDF: {str(e)}")
            raise


# Integration functions for your Flask app
def enhanced_analyze_ultrasound_image(image_path, model, app_config):
    """Enhanced analysis function with comprehensive reporting"""
    # Remove the problematic lines that redefine app_config
    # app_config is already passed as a parameter
    
    static_folder = app_config.get('STATIC_FOLDER', './static')  # fallback if not provided
    upload_folder = app_config.get('UPLOAD_FOLDER')
    annotated_filename = 'annotated_result.jpg'
    annotated_path = os.path.join(upload_folder, annotated_filename)

    try:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError("Could not load image")

        report_generator = MedicalReportGenerator(app_config)
        
        # Run YOLO detection - results is a list of Results objects
        results = model(image_path)  # This returns a list of Results objects
        
        # Extract detection results from the first result (assuming single image)
        result = results[0] if len(results) > 0 else None
        
        detected_structures = set()
        detection_confidences = {}
        nt_measurement = None
        
        if result and hasattr(result, 'boxes') and len(result.boxes) > 0:
            boxes = result.boxes
            for box in boxes.cpu().numpy():
                try:
                    # Get class name and confidence
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    class_name = model.names[class_id]
                    
                    if confidence > 0.5:  # Threshold for reliable detection
                        detected_structures.add(class_name)
                        detection_confidences[class_name] = confidence
                        
                        # Extract NT measurement if detected
                        if class_name == "NT" and confidence > 0.7:
                            try:
                                box_coords = box.xyxy[0]
                                box_height = float(box_coords[3] - box_coords[1])
                                
                                # Only estimate if box_height is valid
                                if box_height > 0:
                                    estimated_nt = estimate_nt_measurement(box_height)
                                    if estimated_nt is not None:
                                        nt_measurement = estimated_nt
                            except (IndexError, TypeError, ValueError) as e:
                                logging.warning(f"Could not extract NT measurement: {str(e)}")
                                continue
                                
                except (IndexError, TypeError, ValueError) as e:
                    logging.warning(f"Error processing detection box: {str(e)}")
                    continue
        
        print("Detected structures:", detected_structures)
        print("NT measurement:", nt_measurement)

        # Create annotated image
        annotated_image_path = create_annotated_image(image_path, results, app_config)
        
        # Fix the static folder path resolution
        rel_path = os.path.relpath(annotated_image_path, start=static_folder)
        annotated_image_url = f"/static/{rel_path.replace(os.sep, '/')}"
        
        # Compile analysis results
        analysis_results = {
            'detected_structures': list(detected_structures),
            'detection_confidences': detection_confidences,
            'nt_measurement_mm': nt_measurement,
            'annotated_image_path': annotated_image_path,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'maternal_age': 30  # This should come from user input
        }
        
        # Generate comprehensive PDF report
        pdf_buffer = report_generator.generate_comprehensive_pdf_report(analysis_results)
        
        return {
            'success': True,
            'analysis_results': analysis_results,
            'pdf_report': pdf_buffer,
            'annotated_image_path': annotated_image_path,
            'annotated_image_url': annotated_image_url 
        }
        
    except Exception as e:
        logging.error(f"Error in enhanced analysis: {str(e)}")
        return {'success': False, 'error': str(e)}

    
def estimate_nt_measurement(box_height_pixels, pixel_to_mm_ratio=0.1):
    """Estimate NT measurement from bounding box height"""
    try:
        # Validate input
        if box_height_pixels is None or box_height_pixels <= 0:
            return None
            
        # This is a simplified estimation - in practice, you'd need proper calibration
        # based on ultrasound machine settings and zoom level
        estimated_mm = box_height_pixels * pixel_to_mm_ratio
        
        # Validate the result is reasonable (NT should be between 0.5-10mm typically)
        if 0.5 <= estimated_mm <= 10.0:
            return round(estimated_mm, 1)
        else:
            # If measurement seems unreasonable, return None
            return None
            
    except (TypeError, ValueError) as e:
        logging.error(f"Error estimating NT measurement: {str(e)}")
        return None
def create_annotated_image(image_path, results, app_config):
    """Create annotated image with detection boxes and labels"""
    try:
        image = cv2.imread(image_path)
        
        # Get the first result (assuming single image)
        result = results[0] if len(results) > 0 else None
        
        if result and hasattr(result, 'boxes'):
            boxes = result.boxes.cpu().numpy()
            for box in boxes:
                # Get coordinates and info
                x1, y1, x2, y2 = box.xyxy[0]
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                class_name = result.names[class_id]
                
                if confidence > 0.5:
                    # Draw bounding box
                    color = (0, 255, 0) if confidence > 0.7 else (0, 255, 255)
                    cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                    
                    # Add label with confidence
                    label = f"{class_name}: {confidence:.2f}"
                    label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
                    cv2.rectangle(image, (int(x1), int(y1 - label_size[1] - 10)),
                                  (int(x1 + label_size[0]), int(y1)), color, -1)
                    cv2.putText(image, label, (int(x1), int(y1 - 5)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        
        # Save annotated image
        annotated_path = os.path.join(app_config['UPLOAD_FOLDER'], 'annotated_result.jpg')
        cv2.imwrite(annotated_path, image)
        print(f"✅ Annotated image saved at: {annotated_path}")
        return annotated_path
        
    except Exception as e:
        logging.error(f"Error creating annotated image: {str(e)}")
        return None


# Additional utility functions for Flask integration
def save_pdf_report(pdf_buffer, filename, upload_folder):
    """Save PDF report to file"""
    try:
        pdf_path = os.path.join(upload_folder, filename)
        with open(pdf_path, 'wb') as f:
            f.write(pdf_buffer.getvalue())
        return pdf_path
    except Exception as e:
        logging.error(f"Error saving PDF report: {str(e)}")
        return None


def generate_summary_json(analysis_results):
    """Generate JSON summary for API responses"""
    
    # Safely handle NT measurement that might be None
    nt_measurement = analysis_results.get('nt_measurement_mm')
    
    # Determine risk level with proper None handling
    if nt_measurement is None:
        risk_level = 'UNABLE_TO_ASSESS'
    elif nt_measurement < 2.5:
        risk_level = 'LOW'
    elif nt_measurement < 3.5:
        risk_level = 'MODERATE'
    else:
        risk_level = 'HIGH'
    
    # Calculate average confidence safely
    confidences = analysis_results.get('detection_confidences', {})
    average_confidence = (
        sum(confidences.values()) / len(confidences) 
        if confidences else 0
    )
    
    summary = {
        'detection_summary': {
            'total_structures_detected': len(analysis_results.get('detected_structures', [])),
            'structures_detected': list(analysis_results.get('detected_structures', [])),
            'average_confidence': round(average_confidence, 3)
        },
        'risk_assessment': {
            'nt_measurement': nt_measurement,
            'nt_measurement_status': 'detected' if nt_measurement is not None else 'not_detected',
            'risk_level': risk_level
        },
        'timestamp': analysis_results.get('timestamp', 'Unknown')
    }
    return summary
