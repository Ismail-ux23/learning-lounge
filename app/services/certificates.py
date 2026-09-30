from io import BytesIO
import qrcode
from flask import current_app
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import landscape,A4

def make_pdf(certificate):
    data=certificate.snapshot; stream=BytesIO(); pdf=canvas.Canvas(stream,pagesize=landscape(A4)); width,height=landscape(A4)
    pdf.setTitle(data['platform']+' — Certificate of Achievement')
    pdf.setAuthor(data['platform'])
    pdf.setFillColor(HexColor('#f6faff'));pdf.rect(0,0,width,height,fill=1,stroke=0)
    pdf.setFillColor(HexColor('#ffffff'));pdf.rect(25,25,width-50,height-50,fill=1,stroke=0)
    pdf.setStrokeColor(HexColor('#bdd5f7'));pdf.setLineWidth(.8);pdf.rect(35,35,width-70,height-70,fill=0,stroke=1)
    # restrained original crystal corner details, all vector paths
    for x,y,scale in [(40,height-42,1),(width-40,42,-1)]:
        pdf.saveState();pdf.translate(x,y);pdf.scale(scale,scale)
        p=pdf.beginPath();p.moveTo(0,0);p.lineTo(60,-12);p.lineTo(24,-65);p.lineTo(0,0)
        pdf.setFillColor(HexColor('#e1eeff'));pdf.setStrokeColor(HexColor('#b2d0fa'));pdf.drawPath(p,fill=1,stroke=1)
        pdf.line(0,0,24,-65);pdf.line(0,0,35,-25);pdf.line(35,-25,60,-12);pdf.line(35,-25,24,-65);pdf.restoreState()
    def line(text,y,size=20,color='#142544',font='Helvetica'):
        pdf.setFillColor(HexColor(color));pdf.setFont(font,size)
        while pdf.stringWidth(text,font,size)>width-130 and size>8: size-=1;pdf.setFont(font,size)
        pdf.drawCentredString(width/2,y,text)
    line(data['platform'],height-88,18,'#315f9e')
    line('CERTIFICATE OF ACHIEVEMENT',height-139,27,'#173d76')
    line('Presented with recognition to',height-186,12,'#647c9d')
    line(data['name'],height-241,36,'#1746b0','Helvetica-Bold')
    pdf.setStrokeColor(HexColor('#dae7f8'));pdf.line(170,height-262,width-170,height-262)
    line(data['course'],height-302,22,'#294e82')
    line(data['type'],height-330,12,'#687f9d')
    line(f"{data['earned']:g} / {data['total']:g} points   |   {data['percent']}%",height-368,19,'#2563eb')
    line('Completed '+certificate.issued.strftime('%d %B %Y'),height-399,12,'#647c9d')
    url=current_app.config['PUBLIC_URL'].rstrip('/')+'/verify/'+certificate.id
    qr=qrcode.make(url);image=BytesIO();qr.save(image,format='PNG');image.seek(0)
    pdf.drawImage(ImageReader(image),width-141,60,73,73)
    pdf.setFillColor(HexColor('#526580'));pdf.setFont('Helvetica',9);pdf.drawString(65,108,'Verification ID: '+certificate.id)
    pdf.setFont('Helvetica',8);pdf.drawString(65,88,'Assessment achievement. No external accreditation is claimed.')
    pdf.setFillColor(HexColor('#5276a6'));pdf.setFont('Helvetica',10);pdf.drawString(65,64,'Powered by Ismail')
    pdf.save();stream.seek(0);return stream
