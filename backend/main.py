from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import razorpay

# Initialize the FastAPI app
app = FastAPI()



#for cors policy, since we are interacting with razorpay api and server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Razorpay client with your API key and secret - we have to generate this manually from razorpay dashboard
client = razorpay.Client(auth=("rzp_test_oh2NWyI3QrMr75", "NLFYIQqZMPe3Wq0XX352b0F3"))

class OrderRequest(BaseModel):
    amount: int
    currency: str
    receipt: str 

class PaymentVerificationRequest(BaseModel):
    razorpay_payment_id: str
    razorpay_order_id: str
    razorpay_signature: str

# Endpoint to create an order
@app.post("/create_order/")
async def create_order(order: OrderRequest):
    try:
        order_data = {
            "amount": order.amount * 100,  # Razorpay requires the amount in paise for processing
            "currency": order.currency,    #amount and currency are inter related to get the particular amount in the particular currency
            "receipt": order.receipt,
            "payment_capture": 1  # Automatically capture the payment
        }
        order_response = client.order.create(data=order_data)
        return order_response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Endpoint to verify payment
@app.post("/verify_payment/")
async def verify_payment(payment: PaymentVerificationRequest):
    try:
        params_dict = {                             #we are getting the payment details from the user and verifying it
            'razorpay_order_id': payment.razorpay_order_id,
            'razorpay_payment_id': payment.razorpay_payment_id,
            'razorpay_signature': payment.razorpay_signature
        }

        # Verify the payment signature
        result = client.utility.verify_payment_signature(params_dict)
        if result:
            return {"status": "Payment successful"}
        else:
            raise HTTPException(status_code=400, detail="Payment verification failed")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))






# To run the FastAPI server, use the following command:
# uvicorn main:app --reload



#use the below command to install the dependencies
#pip install fastapi uvicorn razorpay
