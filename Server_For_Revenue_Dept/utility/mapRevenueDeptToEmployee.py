
from web3 import Web3
import os
import json




def mapRevenueDeptIdToEmployee(revenueDeptId,employeeId):
    
    with open("config.json","r") as f:
        config = json.load(f)

    # Connect to the Ganache network using Web3.py
    ganache_url = config["Ganache_Url"]

    
    web3 = Web3(Web3.HTTPProvider(ganache_url))

    
    # Set the contract deployer address
    web3.eth.default_account = config["Address_Used_To_Deploy_Contract"]



    NETWORK_CHAIN_ID = str(config["NETWORK_CHAIN_ID"])

    landRegistryContract = json.loads(
                open(
                        os.getcwd()+
                        "/../"+"Smart_contracts/build/contracts/"+
                        "LandRegistry.json"
                        ).read()
            )
    


    # Load the contract ABI and address from the compiled contract artifacts
    contract_abi = landRegistryContract["abi"]  # Insert the ABI here

    contract_address = landRegistryContract["networks"][NETWORK_CHAIN_ID]["address"] # Insert the contract address here

    # Create a contract instance using the ABI and address
    contract = web3.eth.contract(abi=contract_abi, address=contract_address)


    # Call the mapRevenueDeptIdToEmployee function with the desired parameters
    revenue_dept_id = revenueDeptId
    employee_address = employeeId  # Insert the employee's Ethereum address here

   
    txn_hash = contract.functions.mapRevenueDeptIdToEmployee(int(revenue_dept_id), employee_address).transact({'from': config["Address_Used_To_Deploy_Contract"]})
       
    # Wait for the transaction to be mined
    print(txn_hash)
    # receipt = web3.eth.waitForTransactionReceipt(txn_hash, timeout=120)
    receipt = web3.eth.get_transaction_receipt(txn_hash)
    print("success")

    # print(web3.toJSON(receipt))
    # successful transaction
    a = 1
    print(receipt)
    if receipt['status'] == 1:
    # if a == 1:
        return True
    else:
        return False
