from flask import Flask, request, url_for, render_template, redirect, session, flash
import requests
from classes import usuario

app = Flask(__name__)
app.secret_key = 'covid19'

usuario1 = usuario.Usuario('admin', 'Odair Coriolano', 'temp1234')
usuario2 = usuario.Usuario('kathy', 'Kathleen Gomes', 'meumozao')

usuarios = { usuario1.id: usuario1, usuario2.id: usuario2}

@app.route('/')
def index():
    return render_template('login.html', titulo='Covid-19 - Login')


@app.route('/dashboard')
def dashboard():
    if session['usuario_logado'] == None:
        return redirect(url_for('index'))
    else:
        url = "https://api.covid19api.com/summary"
        url2 = "https://health-api.com/api/v1/covid-19/countries"
        grafico = [[], []]
        listacovid = []
        paises = []

        try:
            apiresposta = requests.get(url).json()
            for sumario in apiresposta["Countries"]:
                novosdados = {
                    "Pais": sumario["Country"],
                    "NovosConfirmados": sumario["NewConfirmed"],
                    "TotalConfirmados": sumario["TotalConfirmed"],
                    "NovasMortes": sumario["NewDeaths"],
                    "TotalMortes": sumario["TotalDeaths"],
                    "UltimaAtualizacao": sumario["Date"],
                    "Porcentagem": round(sumario["TotalDeaths"] / sumario["TotalConfirmed"],2) if sumario["TotalDeaths"] > 0 else 0
                }
                listacovid.append(novosdados)

            top20 = sorted(listacovid, key=lambda i: i["TotalMortes"], reverse=True)[:20]

            for graph in top20:
                grafico[0].append(graph["Pais"])
                grafico[1].append(graph["TotalMortes"])

        except:
            top20=[]
            print('Erro de conexão a API')
        finally:
            try:
                api2resposta = requests.get(url2).json()
                for pais in api2resposta:
                    novosdados = {
                        "Pais": pais["country"].capitalize(),
                        "Codigo": pais["country_code"]
                    }
                    paises.append(novosdados)
            except:
                print('Erro de conexão à API 2')
            finally:

                if request.args.get('estados'):
                    apiestados = requests.get(request.args.get('estados')).json()
                    pais = request.args.get('pais')

                    if len(apiestados) > 1:
                        return render_template('dashboard.html', titulo='Covid-19 - Dashboard', listacovid=top20,
                                               labels=grafico[0], values=grafico[1], max=grafico[1][0],
                                               paises=sorted(paises, key=lambda i: i["Pais"]), estados=sorted(apiestados, key=lambda i: i["deaths"], reverse=True), nomepais=pais.capitalize())
                    else:
                        flash('Este país não possui um definição de casos por estado')
                        return render_template('dashboard.html', titulo='Covid-19 - Dashboard', listacovid=top20,
                                               labels=grafico[0], values=grafico[1], max=grafico[1][0],
                                               paises=sorted(paises, key=lambda i: i["Pais"]))
                else:
                    return render_template('dashboard.html', titulo='Covid-19 - Dashboard', listacovid=top20, labels=grafico[0], values=grafico[1], max=grafico[1][0], paises=sorted(paises, key=lambda i: i["Pais"]))


@app.route('/autenticar', methods=['POST',])
def autenticar():
    senha = request.form['senha']
    usuario = request.form['usuario']

    if usuario in usuarios:
        if usuarios[usuario].senha == senha:
            session["usuario_logado"] = request.form['usuario']
            flash('Usuário ' + usuarios[usuario].nome + ' logado com sucesso!')
            return redirect(url_for('dashboard'))
    else:
        flash('Usuário ou senha inválidos!')
        return redirect(url_for('index'))

@app.route('/buscapais', methods=['POST',])
def buscapais():
    pais = request.form['pais'][10:15]
    paiscodigo = request.form['pais'][29:31]
    apipais = 'https://health-api.com/api/v1/covid-19/{}/full'.format(paiscodigo)

    return redirect(url_for('dashboard', estados=apipais, pais=pais))

@app.route('/logout')
def logout():
    session['usuario_logado'] = None
    flash('Logout efetuado!!')
    return redirect(url_for('index'))


app.run(debug=True)

