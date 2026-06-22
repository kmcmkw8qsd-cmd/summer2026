from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def login_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            error = "Identifiants incorrects"
    return render(request, 'login.html', {'error': error})

import anthropic  # pip install anthropic

@app.route('/api/regime/estimate-calories', methods=['POST'])
def estimate_calories():
    data = request.get_json()
    meal_text = data.get('meal', '').strip()
    meal_label = data.get('label', 'repas')

    if not meal_text:
        return jsonify({'kcal': 0, 'detail': ''}), 200

    client = anthropic.Anthropic()  # utilise ANTHROPIC_API_KEY automatiquement

    prompt = f"""Tu es un nutritionniste expert. Estime le nombre total de calories (kcal) pour ce {meal_label} :
"{meal_text}"

Réponds UNIQUEMENT avec un objet JSON valide, sans texte avant ni après, sans balises markdown :
{{"kcal": 450, "detail": "2 œufs (140) + pain complet (120) + thé (0) + beurre (90)"}}

- kcal : estimation totale arrondie à la dizaine
- detail : décomposition courte par aliment (max 80 caractères)
- Base-toi sur des portions moyennes si les quantités ne sont pas précisées"""

    try:
        message = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = message.content[0].text.strip()
        import json, re
        clean = re.sub(r'```json|```', '', raw).strip()
        parsed = json.loads(clean)
        return jsonify(parsed), 200
    except Exception as e:
        print(f"Erreur estimation calories: {e}")
        return jsonify({'error': str(e)}), 500

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required(login_url='/')
def home(request):
    return render(request, 'home.html')

@login_required(login_url='/')
def dashboard(request):
    return render(request, 'dashboard.html')

@login_required(login_url='/')
def deen(request):
    return render(request, 'deen.html')

@login_required(login_url='/')
def sport(request):
    return render(request, 'sport.html')

@login_required(login_url='/')
def regime(request):
    return render(request, 'regime.html')

@login_required(login_url='/')
def learning(request):
    return render(request, 'learning.html')

@login_required(login_url='/')
def selfcare(request):
    return render(request, 'selfcare.html')

@login_required(login_url='/')
def homecare(request):
    return render(request, 'homecare.html')

def goals(request):
    return render(request, 'goals.html')