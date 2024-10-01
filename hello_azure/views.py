from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.http import JsonResponse

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

import stripe
import os

def index(request):
    print('Request for index page received')
    return render(request, 'hello_azure/index.html')

def standalone_button(request):
    print('Payment')
    return render(request, 'hello_azure/standalone button.html')

def redirect_button (request):
    return render(request, 'hello_azure/redirect_button.html')

stripe.api_key = 'sk_test_51Q2xbFHo2S95esHCvZllu2zMvO1z9911eTiCC5wxtNenRjqSOAH5jiXXN2k2MMh350lFp4bXtlHpKiOmDCSfySDo006uCsuZZZ'

@csrf_exempt
def hello(request):
    ###
    # Testing for getting key vault
    ###

    print('----- Before setting')

    # Replace with your Key Vault URL
    key_vault_url = "https://exemplar-test-value.vault.azure.net/"

    print('----- Before DefaultAzureCredential')

    # Initialize the DefaultAzureCredential (uses environment variables or managed identity)
    credential = DefaultAzureCredential()

    print('----- Before SecretClient')

    # Create a SecretClient using the URL and credentials
    secret_client = SecretClient(vault_url=key_vault_url, credential=credential)

    # Replace with your secret name
    secret_name = "exemplar-test-key"

    print('----- Before get_secret')

    try:
    # Retrieve the secret
        retrieved_secret = secret_client.get_secret(secret_name)
    except Exception as e:
        print("Error retrieving secret:", str(e))
        # Handle the error, e.g., log it, retry, or raise a custom exception
    
    print('----- After get_secret')

    secret_value = retrieved_secret.value

    # Print the secret value
    print(f"Secret value: {secret_value}")

    print('----- hello ----- ')


    if request.method == 'POST':
        name = request.POST.get('name')
        
        if name is None or name == '':
            print("Request for hello page received with no name or blank name -- redirecting")
            return redirect('index')
        else:
            print("Request for hello page received with name=%s" % name)
            context = {'name': name + ' ' + secret_value }
            return render(request, 'hello_azure/hello.html', context)
    else:
        return redirect('index')
    
@csrf_exempt
def create_checkout_session(request):
    # Replace with your Stripe API key
    # stripe.api_key = 'sk_test_5102xbFHo2595esHCvZ...mDCSfySD0006uCsuZZZ'
    # 'pk_test_51Q2xbFHo2S95esHChBBAXVc5S4cLHhoijzrn1mHNQAAYz6spsGh7ZZBNSLCiDhcC0iO81eckipjOuInwFdIJuiTW00ThNqk0au'
    
    # domain_url = os.getenv('DOMAIN')
    domain_url='http://localhost:8000'

    session = stripe.checkout.Session.create(
        line_items=[
            {
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'T-shirt',
                    },
                    'unit_amount': 2000,
                },
                'quantity': 1,
            }
        ],
        mode='payment',

        # success_url=reverse('success'),
        # cancel_url=reverse('cancel'),
        success_url=domain_url + '/success?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=domain_url + '/canceled',
        
    )

    return redirect(session.url, code=303)

# http://localhost:3000/success?session_id=cs_test_a1mfCVlZiJuQ5OKR1JFIoafDHR19DEGD2M3GSiArUfT1v2fhDXH2xZHKN6
def success(request):
    id = request.GET.get('session_id')
    checkout_session = stripe.checkout.Session.retrieve(id)
    return JsonResponse(checkout_session)

    
def cancel(request):
    sample_data = {
        "status": "canceled",
        "message": "This is a sample JSON response with a canceled status.",
    }
    return JsonResponse(sample_data)
