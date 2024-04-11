from distutils import errors
from flask import Flask, jsonify,render_template,request,Response, send_file
from pymongo import MongoClient
from pymongo.errors import PyMongoError
import gridfs
from web3 import Web3, HTTPProvider
import json
import os

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib import colors

# blockchain Network ID
NETWORK_CHAIN_ID = "5777"




# connect to mong db
client = MongoClient('mongodb://localhost:27017')

# connect to database
LandRegistryDB = client.LandRegistry

# connect to file System
fs = gridfs.GridFS(LandRegistryDB)

# connect to collection
propertyDocsTable = LandRegistryDB.Property_Docs



app = Flask(
    __name__,
    static_url_path='', 
    static_folder='web/static',
    template_folder='web/templates'
)





@app.route('/')
def index():
    # Render the 'index.html' template with the variables passed in
    return render_template('index.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html',add_property=True)

@app.route('/download_pdf', methods = ['POST'])
def download_pdf():
    print("start pdf")
    print(request.form)
    name =  request.form['name']
    propertyId =  request.form['propertyId']
    locationId =  request.form['locationId']
    revenueDepartmentId = request.form['revenueDepartmentId']
    surveyNumber = request.form['surveyNumber']
    area = request.form['area']
    varification = request.form['Varification']
    file_name = "PrtCertificate" + propertyId + ".pdf"
    certificateNumber = "L" + locationId + "P" + propertyId + "SN" + surveyNumber

    doc = SimpleDocTemplate(file_name, pagesize=letter)
    styles = getSampleStyleSheet()

    # Custom styles
    header_style = ParagraphStyle(name='HeaderStyle', parent=styles['Heading1'], alignment=1)
    footer_style = ParagraphStyle(name='FooterStyle', parent=styles['Normal'], alignment=1)

    # Content
    content = []
    content.append(Paragraph("<center><h1 style='font-size:30px'>Land Certificate</h1></center>", header_style))
    content.append(Spacer(1, 12))
    content.append(HRFlowable(width="100%", color=colors.black))
    content.append(HRFlowable(width="100%", color=colors.black))
    content.append(Spacer(1, 12))
    content.append(Paragraph("<b>Certificate No.:</b> " + certificateNumber, styles['Normal']))
    content.append(Paragraph("<b>Certificate Issue Date:</b> 12/march/2023", styles['Normal']))
    content.append(Paragraph("<b>Property ID :</b> " + propertyId, styles['Normal']))
    content.append(Paragraph("<b>Location ID :</b> " + locationId, styles['Normal']))
    content.append(Paragraph("<b>Owner of land:</b> " + name, styles['Normal']))
    content.append(Paragraph("<b>Revenue DepartmentID:</b> " + revenueDepartmentId, styles['Normal']))
    content.append(Paragraph("<b>Survey Number:</b> " + surveyNumber, styles['Normal']))
    content.append(Paragraph("<b>Area:</b> " + area + "msq.", styles['Normal']))
    content.append(Paragraph("<b>Varification Status: </b>" + varification, styles['Normal']))
    content.append(Spacer(1, 12))
    content.append(Paragraph("<b>Disclaimer</b>", styles['Normal']))
    content.append(Paragraph("System generated certificate seal and signature not required.", styles['Normal']))
    content.append(Spacer(1, 12))
    content.append(Paragraph("This PDF is generated by a blockchain-based land registration system developed by students of the Information Technology Department at Government College of Engineering, Chh. Sambhajinagar, Maharashtra, including Praful Chalakh, Vaibhav Jagtap, Prajwal Shinde, and Ajit Tiwari, as part of their final year major project coursework.", styles['Normal']))
    content.append(Spacer(1, 12))
    content.append(Paragraph("<hr width='100%' align='center' color='black' size='1'>", styles['Normal']))
    content.append(Paragraph("<hr width='100%' align='center' color='black' size='1'>", styles['Normal']))
    content.append(Paragraph("End of Certificate", footer_style))
    print("code executed")
    doc.build(content)
    return send_file(file_name, as_attachment=True)
    print("sucessfully!!")


@app.route('/uploadPropertyDocs', methods=['GET', 'POST'])
def upload():
    # Get the uploaded files and form data from the request
    registraionDocs = request.files['propertyDocs']
    owner = request.form['owner']
    # propertyId = request.form['propertyId']
    # location = request.form['location']
    revenueDeptId = request.form['revenueDeptId']
    surveyNo = request.form['surveyNo']
    area = request.form['area']
    contractABI = request.form['contractABI']
    contractAddress = request.form['contractAddress']
    contract = request.form['contract']
    accountUsedToLogin = request.form['accountUsedToLogin']
    # Do something with the uploaded files and form data
    propertyId = "NOT_ASSIGN"
    status = "Pending"

    try:
        file_id = fs.put(registraionDocs, filename="%s_%s.pdf"%(owner, propertyId))
        rowId = propertyDocsTable.insert_one({
                                            "Status": status,
                                            "Owner":owner,
                                            "Property_Id":propertyId,
                                            #"location": location,
                                            "revenueDeptId": revenueDeptId,
                                            "surveyNo": surveyNo,
                                            "area": area,
                                            "contractABI": contractABI,
                                            "contractAddress": contractAddress,
                                            "contract": contract,
                                            "accountUsedToLogin": accountUsedToLogin,
                                            "%s_%s.pdf"%(owner, propertyId):file_id
                                        }).inserted_id

    except errors.PyMongoError as e:
        # Return a response to the client
        return jsonify({'status': 'Failed Uploading Files','fileId':str(0)})
    else:
        return jsonify({'status': 'success','fileId':str(file_id)})
    
                                    

@app.route('/propertiesDocs/pdf/<propertyId>')
def get_pdf(propertyId):
  try:
    try:
        propertyDetails = propertyDocsTable.find({"Property_Id":"%s"%(propertyId)})[0]
        
    except IndexError as e:
        return jsonify({"status":0,"Reason":"No Property Matched With Id"})

    fileName = "%s_%s.pdf"%(propertyDetails['Owner'],propertyDetails['Property_Id'])
    
    file = fs.get(propertyDetails[fileName])

    response = Response(file, content_type='application/pdf')
    response.headers['Content-Disposition'] = f'inline; filename="{file.filename}"'
    
    return response

  except Exception as e:
    return jsonify({"status":0,"Reason":str(e)})




@app.route('/fetchContractDetails')
def fetchContractDetails():
    usersContract = json.loads(
            open(
                    os.getcwd()+
                    "/../"+"Smart_contracts/build/contracts/"+
                    "Users.json"
                    ).read()
        )
    
    landRegistryContract = json.loads(
            open(
                    os.getcwd()+
                    "/../"+"Smart_contracts/build/contracts/"+
                    "LandRegistry.json"
                    ).read()
        )

    transferOwnerShip = json.loads(
            open(
                    os.getcwd()+
                    "/../"+"Smart_contracts/build/contracts/"+
                    "TransferOwnerShip.json"
                    ).read()
        )

    response = {}

    response["Users"] = {}
    response["Users"]["address"] = usersContract["networks"][NETWORK_CHAIN_ID]["address"]
    response["Users"]["abi"] = usersContract["abi"]

    response["LandRegistry"]  = {}
    response["LandRegistry"]["address"] = landRegistryContract["networks"][NETWORK_CHAIN_ID]["address"]
    response["LandRegistry"]["abi"] = landRegistryContract["abi"]

    response["TransferOwnership"]  = {}
    response["TransferOwnership"]["address"] = transferOwnerShip["networks"][NETWORK_CHAIN_ID]["address"]
    response["TransferOwnership"]["abi"] = transferOwnerShip["abi"]


    return response


@app.route('/logout')
def logout():
    return redirect('/')

@app.route('/availableToBuy')
def availableToBuy():
    return render_template('availableToBuy.html')

@app.route('/MySales')
def MySales():
    return render_template('mySales.html')

@app.route('/myRequestedSales')
def myRequestedSales():
    return render_template('myRequestedSales.html')

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
