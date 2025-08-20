from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, make_response
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import requests
import psycopg2
import re

def crear_tablas():
    try:
        connection = psycopg2.connect(
            host="localhost",
            database="ecomont",
            user="postgres",      # cambiá si usás otro usuario
            password="1234"
        )
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                descripcion TEXT,
                precio NUMERIC(10, 2),
                stock INTEGER
            );
        """)

        connection.commit()
        cursor.close()
        connection.close()
    except Exception as e:
        print("❌ Error al crear la tabla:", e)


app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'  # Necesario para flash messages

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost:5432/ecomont' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class ReporteCiudadano(db.Model):
    __tablename__ = 'reportes_ciudadanos'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    ubicacion = db.Column(db.String(300))
    estado = db.Column(db.String(50), default='Pendiente')
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    imagen = db.Column(db.Text)
    tipo = db.Column(db.String(50))
    urgencia = db.Column(db.String(20), default='baja')
    contacto = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def latitud(self):
        """Extrae la latitud desde la columna ubicacion"""
        if not self.ubicacion:
            return None
        
        # Buscar patrón "Lat: -27.177779"
        match = re.search(r'Lat:\s*(-?\d+\.?\d*)', self.ubicacion)
        if match:
            return float(match.group(1))
        
        # Buscar patrón "-27.167900, -65.501700" (lat primera)
        match = re.search(r'^(-?\d+\.?\d*),\s*(-?\d+\.?\d*)$', self.ubicacion.strip())
        if match:
            return float(match.group(1))
        
        return None
    
    @property
    def longitud(self):
        """Extrae la longitud desde la columna ubicacion"""
        if not self.ubicacion:
            return None
        
        # Buscar patrón "Lng: -65.509786"
        match = re.search(r'Lng:\s*(-?\d+\.?\d*)', self.ubicacion)
        if match:
            return float(match.group(1))
        
        # Buscar patrón "-27.167900, -65.501700" (lng segunda)
        match = re.search(r'^(-?\d+\.?\d*),\s*(-?\d+\.?\d*)$', self.ubicacion.strip())
        if match:
            return float(match.group(2))
        
        return None

class InformeDefensaCivil(db.Model):
    __tablename__ = 'informes_defensa_civil'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    ubicacion = db.Column(db.String(300))
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    creado_por = db.Column(db.String(100), default="Defensa Civil")



# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================
def obtener_clima(ciudad='Monteros', api_key='361760d7c4370eb2ebff3b223d17cd4b'):
    url = f'https://api.openweathermap.org/data/2.5/weather?q={ciudad},ar&units=metric&lang=es&appid={api_key}'
    try:
        respuesta = requests.get(url)
        datos = respuesta.json()
        clima = {
            'temp': round(datos['main']['temp']),
            'descripcion': datos['weather'][0]['description'].capitalize(),
            'icono': datos['weather'][0]['icon'],
            'ciudad': datos['name']
        }
        return clima
    except Exception as e:
        print("Error al obtener el clima:", e)
        return None

# =============================================================================
# RUTAS PRINCIPALES
# =============================================================================
@app.route('/')
def inicio():
    return render_template('inicio.html')

# =============================================================================
# RUTAS CIUDADANO
# =============================================================================
@app.route('/login_ciudadano', methods=['GET', 'POST'])
def login_ciudadano():
    if request.method == 'POST':
        return redirect(url_for('dashboard_ciudadano'))
    try:
        return render_template('ciudadano/login_ciudadano.html')
    except:
        return render_template('login_ciudadano.html')



@app.route('/dashboard_ciudadano')
def dashboard_ciudadano():
    try:
        reportes = ReporteCiudadano.query.all()
        reportes_pendientes = ReporteCiudadano.query.filter_by(estado='Pendiente').count()
        reportes_resueltos = ReporteCiudadano.query.filter_by(estado='Resuelto').count()
        
        return render_template('ciudadano/dashboard_ciudadano.html', 
                             reportes=reportes,
                             reportes_pendientes=reportes_pendientes,
                             reportes_resueltos=reportes_resueltos)
    except:
        reportes = ReporteCiudadano.query.all()
        return render_template('dashboard_ciudadano.html', reportes=reportes)



    
@app.route('/asistente_ia')
def asistente_ia():
    try:
        return render_template('ciudadano/asistente_ia.html')
    except:
        return render_template('asistente_ia.html')

@app.route('/estadisticas_ia')
def estadisticas_ia():
    return render_template('ciudadano/estadisticas_ia.html')


@app.route('/nuevo_reporte', methods=['GET', 'POST'])
def nuevo_reporte():
    if request.method == 'POST':
        try:
            # Construir ubicacion con coordenadas si las envían
            ubicacion = request.form.get('ubicacion', '')
            latitud = request.form.get('latitud')
            longitud = request.form.get('longitud')
            
            # Si hay coordenadas, las agregamos al formato de ubicacion
            if latitud and longitud:
                ubicacion = f"Lat: {latitud}, Lng: {longitud}"
            
            nuevo = ReporteCiudadano(
                titulo=request.form.get('titulo', ''),
                descripcion=request.form.get('descripcion', ''),
                ubicacion=ubicacion,
                tipo=request.form.get('tipo', ''),
                urgencia=request.form.get('urgencia', 'baja'),
                contacto=request.form.get('contacto', '')
            )
            db.session.add(nuevo)
            db.session.commit()
            flash('¡Reporte creado exitosamente!', 'success')
            return redirect(url_for('ver_reportes'))
        except Exception as e:
            db.session.rollback()
            print(f"Error al crear reporte: {str(e)}")
            flash('Error al crear el reporte', 'error')
    
    try:
        return render_template('ciudadano/nuevo_reporte.html')
    except:
        return render_template('nuevo_reporte.html')
 
@app.route('/ver_reportes')
def ver_reportes():
    reportes = ReporteCiudadano.query.order_by(ReporteCiudadano.fecha.desc()).all()
    try:
        return render_template('ciudadano/ver_reportes.html', 
                               reportes=reportes, 
                               current_year=datetime.now().year)
    except:
        return render_template('ver_reportes.html', 
                               reportes=reportes, 
                               current_year=datetime.now().year)

@app.route('/mis_reportes')
def mis_reportes():
    return redirect(url_for('ver_reportes'))

@app.route('/editar_reporte/<int:reporte_id>', methods=['GET', 'POST'])
def editar_reporte(reporte_id):
    reporte = ReporteCiudadano.query.get_or_404(reporte_id)
    
    if request.method == 'POST':
        try:
            # Construir ubicacion con coordenadas si las envían
            ubicacion = request.form.get('ubicacion', reporte.ubicacion)
            latitud = request.form.get('latitud')
            longitud = request.form.get('longitud')
            
            # Si hay coordenadas nuevas, las agregamos al formato de ubicacion
            if latitud and longitud:
                ubicacion = f"Lat: {latitud}, Lng: {longitud}"
            
            reporte.titulo = request.form.get('titulo', reporte.titulo)
            reporte.descripcion = request.form.get('descripcion', reporte.descripcion)
            reporte.ubicacion = ubicacion
            reporte.updated_at = datetime.utcnow()
            
            db.session.commit()
            flash('¡Reporte actualizado exitosamente!', 'success')
            return redirect(url_for('ver_reportes'))
        except Exception as e:
            db.session.rollback()
            print(f"Error al actualizar reporte: {str(e)}")
            flash('Error al actualizar el reporte', 'error')
    
    try:
        return render_template('ciudadano/editar_reporte.html', reporte=reporte)
    except:
        return render_template('editar_reporte.html', reporte=reporte)

@app.route('/eliminar_reporte/<int:reporte_id>', methods=['POST'])
def eliminar_reporte(reporte_id):
    try:
        reporte = ReporteCiudadano.query.get_or_404(reporte_id)
        titulo_reporte = reporte.titulo
        
        db.session.delete(reporte)
        db.session.commit()
        
        flash(f'Reporte \"{titulo_reporte}\" eliminado exitosamente', 'success')
        print(f"Reporte {reporte_id} eliminado de la base de datos")
        
    except Exception as e:
        db.session.rollback()
        print(f"Error al eliminar reporte {reporte_id}: {str(e)}")
        flash('Error al eliminar el reporte', 'error')
    
    return redirect(url_for('ver_reportes'))

# =============================================================================
# RUTAS MUNICIPALIDAD
# =============================================================================
@app.route('/login_municipalidad', methods=['GET', 'POST'])
def login_municipalidad():
    if request.method == 'POST':
        return redirect(url_for('dashboard_municipalidad'))
    try:
        return render_template('municipalidad/login_municipalidad.html')
    except:
        return render_template('login_municipalidad.html')

# ¡ESTA ES LA ÚNICA RUTA PARA DASHBOARD MUNICIPALIDAD!
@app.route('/dashboard_municipalidad')
def dashboard_municipalidad():
    try:
        return render_template('municipalidad/dashboard_municipalidad.html')
    except:
        return render_template('dashboard_municipalidad.html')

@app.route('/gestionar_reportes')
def gestionar_reportes():
    return render_template('municipalidad/gestionar_reportes.html')

@app.route('/emitir_mensaje')
def emitir_mensaje():
    return render_template('municipalidad/emitir_mensaje.html')

@app.route('/ver_reportesM')
def ver_reportesM():
    return render_template('municipalidad/ver_reportesM.html')

@app.route('/inicio_municipalidad')
def inicio_municipalidad():
    return render_template('inicio.html')

# =============================================================================
# RUTAS DEFENSA CIVIL
# =============================================================================
@app.route('/login_defensa', methods=['GET', 'POST'])
def login_defensa():
    if request.method == 'POST':
        return redirect(url_for('dashboard_defensa'))
    try:
        return render_template('defensa/login_defensa.html')
    except:
        return render_template('login_defensa.html')

@app.route('/dashboard_defensa')
def dashboard_defensa():
    clima = obtener_clima()
    total_urgentes = ReporteCiudadano.query.filter_by(urgencia='alta').filter(ReporteCiudadano.estado != 'Resuelto por Defensa Civil').count()
    total_resueltas = ReporteCiudadano.query.filter_by(estado='Resuelto por Defensa Civil').count()
    reportes = ReporteCiudadano.query.filter_by(urgencia='alta').filter(ReporteCiudadano.estado != 'Resuelto por Defensa Civil').all()

    return render_template('defensa/dashboard_defensa.html',
                           clima=clima,
                           total_urgentes=total_urgentes,
                           total_resueltas=total_resueltas,
                           reportes=reportes)


@app.route('/alertas_urgentes')
def alertas_urgentes():
    urgentes_raw = ReporteCiudadano.query.filter_by(urgencia='alta') \
        .filter(ReporteCiudadano.estado != 'Resuelto por Defensa Civil') \
        .order_by(ReporteCiudadano.fecha.desc()).all()

    # Convertir a dict para usar tojson en la plantilla
    urgentes = []
    for r in urgentes_raw:
        urgentes.append({
            'id': r.id,
            'titulo': r.titulo,
            'descripcion': r.descripcion,
            'ubicacion': r.ubicacion,
            'estado': r.estado,
            'fecha': r.fecha.strftime('%Y-%m-%d %H:%M') if r.fecha else '',
            'tipo': r.tipo,
            'urgencia': r.urgencia,
            'contacto': r.contacto,
            'imagen': r.imagen
        })

    return render_template('defensa/alertas_urgentes.html', reportes=urgentes)


@app.route('/resolver_alerta/<int:reporte_id>', methods=['POST', 'GET'])
def resolver_alerta(reporte_id):
    try:
        reporte = ReporteCiudadano.query.get_or_404(reporte_id)
        reporte.estado = "Resuelto por Defensa Civil"
        reporte.updated_at = datetime.utcnow()
        db.session.commit()

        return redirect(url_for('nuevo_informe_defensa', 
                            titulo=reporte.titulo, 
                            descripcion=reporte.descripcion, 
                            ubicacion=reporte.ubicacion))
    except Exception as e:
        db.session.rollback()
        print(f"Error al resolver alerta: {str(e)}")
        flash('Error al resolver el reporte', 'error')
        return redirect(url_for('alertas_urgentes'))

@app.route('/nuevo_informe_defensa', methods=['GET', 'POST'])
def nuevo_informe_defensa():
    if request.method == 'POST':
        try:
            nuevo = InformeDefensaCivil(
                titulo=request.form.get('titulo', ''),
                descripcion=request.form.get('descripcion', ''),
                ubicacion=request.form.get('ubicacion', ''),
                fecha=datetime.utcnow(),
                creado_por='Defensa Civil'
            )
            db.session.add(nuevo)
            db.session.commit()
            flash('¡Informe creado exitosamente!', 'success')
            return redirect(url_for('historial_defensa'))

        except Exception as e:
            db.session.rollback()
            print(f"Error al crear informe: {str(e)}")
            flash('Error al crear el informe', 'error')
    
    return render_template('defensa/nuevo_informe_defensa.html')


@app.route('/historial_defensa')
def historial_defensa():
    informes = InformeDefensaCivil.query.order_by(InformeDefensaCivil.fecha.desc()).all()
    return render_template('defensa/historial_defensa.html', informes=informes)



@app.route('/zona_critica')
def zona_critica():
    zona = {
        'ubicacion': 'Canal San Juan, zona oeste',
        'problema': 'Riesgo de desborde por acumulación de residuos y lluvias intensas',
        'recomendacion': 'Monitorear cada 4 horas y reforzar señalización'
    }
    return render_template('defensa/zona_critica.html', zona=zona)

@app.route('/mapa_alertas_defensa')
def mapa_alertas_defensa():
    urgentes = ReporteCiudadano.query.filter_by(urgencia='alta').all()

    alertas_mapa = []
    for r in urgentes:
        if r.latitud and r.longitud:
            alertas_mapa.append({
                "titulo": r.titulo,
                "tipo": r.tipo,
                "estado": r.estado,
                "ubicacion": r.ubicacion,
                "lat": r.latitud,
                "lng": r.longitud,
                "fecha": r.fecha.strftime('%Y-%m-%d %H:%M')
            })

    return render_template('defensa/mapa_alertas_defensa.html', alertas=alertas_mapa)

# =============================================================================
# APIs PARA REPORTES CIUDADANOS
# =============================================================================
@app.route('/api/reportes', methods=['GET'])
def obtener_reportes():
    try:
        reportes = ReporteCiudadano.query.all()
        
        reportes_list = []
        for reporte in reportes:
            reportes_list.append({
                'id': reporte.id,
                'titulo': reporte.titulo,
                'descripcion': reporte.descripcion,
                'ubicacion': reporte.ubicacion,
                'latitud': reporte.latitud,  # Ahora usa la propiedad
                'longitud': reporte.longitud,  # Ahora usa la propiedad
                'estado': reporte.estado,
                'fecha': reporte.fecha.strftime('%Y-%m-%d %H:%M:%S'),
                'tipo': reporte.tipo,
                'urgencia': reporte.urgencia,
                'contacto': reporte.contacto,
                'imagen': reporte.imagen
            })
        
        return jsonify({
            'success': True,
            'reportes': reportes_list,
            'total': len(reportes_list)
        })
    
    except Exception as e:
        print(f"Error al obtener reportes: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/reportes/<int:id>/estado', methods=['PUT'])
def actualizar_estado_reporte(id):
    try:
        reporte = ReporteCiudadano.query.get_or_404(id)
        data = request.get_json()
        
        if 'estado' in data:
            reporte.estado = data['estado']
            reporte.updated_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Estado actualizado correctamente'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Estado no proporcionado'
            }), 400
    
    except Exception as e:
        print(f"Error al actualizar estado: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/reporte/<int:reporte_id>')
def get_reporte_api(reporte_id):
    try:
        reporte = ReporteCiudadano.query.get_or_404(reporte_id)
        
        fecha_formateada = reporte.fecha.strftime('%d/%m/%Y a las %H:%M') if reporte.fecha else 'Sin fecha'
        
        response_data = {
            'id': reporte.id,
            'titulo': reporte.titulo,
            'descripcion': reporte.descripcion,
            'ubicacion': reporte.ubicacion,
            'latitud': reporte.latitud,  # Ahora usa la propiedad
            'longitud': reporte.longitud,  # Ahora usa la propiedad
            'estado': reporte.estado,
            'fecha': fecha_formateada,
            'imagen': reporte.imagen,
            'tipo': reporte.tipo,
            'urgencia': reporte.urgencia,
            'contacto': reporte.contacto
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error al obtener reporte {reporte_id}: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# Ruta para debugging
@app.route('/debug/reportes')
def debug_reportes():
    reportes = ReporteCiudadano.query.all()

    reportes_data = [{
        'id': r.id,
        'titulo': r.titulo,
        'descripcion': r.descripcion,
        'ubicacion': r.ubicacion,
        'latitud': r.latitud,  # Ahora usa la propiedad
        'longitud': r.longitud,  # Ahora usa la propiedad
        'estado': r.estado,
        'tipo': r.tipo,
        'urgencia': r.urgencia,
        'contacto': r.contacto
    } for r in reportes]

    return jsonify({
        'reportes_ciudadanos': {
            'total': len(reportes_data),
            'reportes': reportes_data
        }
    })

# =============================================================================
# MANEJO DE ERRORES
# =============================================================================
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Página no encontrada'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Error interno del servidor'}), 500

# =============================================================================
# EJECUCIÓN PRINCIPAL
# =============================================================================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ Conexión exitosa a la base de datos")
    app.run(debug=True, host='0.0.0.0', port=5000)



# =============================================================================
# RUTAS DE IA PARA CIUDADANOS
# =============================================================================


import json
from datetime import datetime, timedelta

# Configuración de OpenAI (puedes usar una API key gratuita o mock)
# openai.api_key = "tu-api-key-aqui"  # Descomenta cuando tengas la key

@app.route('/asistente_ia')
def asistente_ia():
    """Página principal del asistente IA"""
    try:
        return render_template('ciudadano/asistente_ia.html')
    except:
        return render_template('asistente_ia.html')

@app.route('/api/clasificar_reporte', methods=['POST'])
def clasificar_reporte():
    """IA para clasificar automáticamente el tipo de reporte"""
    try:
        data = request.get_json()
        titulo = data.get('titulo', '')
        descripcion = data.get('descripcion', '')
        
        # Lógica simple de clasificación (mock de IA)
        texto_completo = (titulo + " " + descripcion).lower()
        
        clasificacion = {
            'tipo': 'otro',
            'urgencia': 'baja',
            'confianza': 0.85,
            'sugerencias': []
        }
        
        # Clasificación por palabras clave
        if any(palabra in texto_completo for palabra in ['basura', 'desperdicios', 'residuos', 'bolsas', 'contenedor']):
            clasificacion['tipo'] = 'basura'
            clasificacion['confianza'] = 0.92
            clasificacion['sugerencias'].append('Incluí la dirección exacta del contenedor')
            
        elif any(palabra in texto_completo for palabra in ['agua', 'inundacion', 'charco', 'lluvia', 'desague']):
            clasificacion['tipo'] = 'agua'
            clasificacion['confianza'] = 0.88
            if any(palabra in texto_completo for palabra in ['urgente', 'emergencia', 'grave']):
                clasificacion['urgencia'] = 'alta'
            
        # Detectar urgencia
        if any(palabra in texto_completo for palabra in ['emergencia', 'urgente', 'peligro', 'grave', 'riesgo']):
            clasificacion['urgencia'] = 'alta'
            clasificacion['sugerencias'].append('Este reporte será enviado a Defensa Civil')
            
        return jsonify({
            'success': True,
            'clasificacion': clasificacion
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/sugerir_ubicacion', methods=['POST'])
def sugerir_ubicacion():
    """IA para sugerir mejoras en la descripción de ubicación"""
    try:
        data = request.get_json()
        ubicacion = data.get('ubicacion', '').lower()
        
        sugerencias = []
        
        if len(ubicacion) < 10:
            sugerencias.append('Agregá más detalles: altura, esquina, referencias cercanas')
            
        if 'centro' in ubicacion and 'plaza' not in ubicacion:
            sugerencias.append('¿Está cerca de Plaza San Martín?')
            
        if not any(num.isdigit() for num in ubicacion):
            sugerencias.append('Incluí la altura o número de la dirección si es posible')
            
        lugares_conocidos = [
            {'original': 'terminal', 'sugerencia': 'Terminal de Ómnibus'},
            {'original': 'municipalidad', 'sugerencia': 'Edificio Municipal'},
            {'original': 'plaza', 'sugerencia': 'Plaza San Martín'},
            {'original': 'hospital', 'sugerencia': 'Hospital Regional'},
        ]
        
        for lugar in lugares_conocidos:
            if lugar['original'] in ubicacion:
                sugerencias.append(f'Referencia: {lugar["sugerencia"]}')
        
        return jsonify({
            'success': True,
            'sugerencias': sugerencias[:3]  # Máximo 3 sugerencias
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/generar_reporte_sugerido', methods=['POST'])
def generar_reporte_sugerido():
    """IA para mejorar la redacción del reporte"""
    try:
        data = request.get_json()
        titulo = data.get('titulo', '')
        descripcion = data.get('descripcion', '')
        
        # Mock de mejora de texto
        titulo_mejorado = titulo
        descripcion_mejorada = descripcion
        
        # Mejorar título
        if len(titulo) < 20:
            tipo_detectado = "contaminación ambiental"
            if 'basura' in titulo.lower():
                tipo_detectado = "acumulación de residuos"
            elif 'agua' in titulo.lower():
                tipo_detectado = "problema hídrico"
                
            titulo_mejorado = f"Reporte de {tipo_detectado} - {titulo}"
        
        # Mejorar descripción
        if len(descripcion) < 50:
            descripcion_mejorada += "\n\nDetalles adicionales sugeridos:\n"
            descripcion_mejorada += "- Tiempo aproximado desde que se detectó el problema\n"
            descripcion_mejorada += "- Impacto en la comunidad\n"
            descripcion_mejorada += "- Posibles causas observadas"
        
        return jsonify({
            'success': True,
            'sugerencias': {
                'titulo': titulo_mejorado,
                'descripcion': descripcion_mejorada,
                'mejoras': [
                    'Título más descriptivo',
                    'Estructura organizada',
                    'Información adicional sugerida'
                ]
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chat_asistente', methods=['POST'])
def chat_asistente():
    """Chat con asistente IA para ayuda"""
    try:
        data = request.get_json()
        mensaje = data.get('mensaje', '').lower()
        
        # Respuestas predefinidas (mock de IA)
        respuestas = {
            'como reportar': 'Para hacer un reporte: 1) Hacé clic en "Nuevo Reporte", 2) Completá el título y descripción, 3) Agregá la ubicación, 4) Seleccioná el tipo y urgencia, 5) Enviá el reporte.',
            'que tipo urgencia': 'Urgencia BAJA: problemas que pueden esperar. MEDIA: requiere atención pronta. ALTA: emergencias que van directo a Defensa Civil.',
            'como seguir reporte': 'Podés ver el estado de tus reportes en "Mis Reportes". Te notificaremos cuando cambien de estado.',
            'que fotos subir': 'Subí fotos claras del problema. Máximo 5 fotos de 5MB cada una. Las fotos ayudan a entender mejor la situación.',
            'cuanto tarda': 'Los reportes normales se responden en 24-48 horas. Los de urgencia alta van inmediatamente a Defensa Civil.',
        }
        
        respuesta = "No entendí tu consulta. ¿Podrías ser más específico? Puedo ayudarte con: cómo reportar, tipos de urgencia, seguimiento de reportes, fotos, y tiempos de respuesta."
        
        for clave, resp in respuestas.items():
            if any(palabra in mensaje for palabra in clave.split()):
                respuesta = resp
                break
        
        return jsonify({
            'success': True,
            'respuesta': respuesta,
            'sugerencias': [
                '¿Cómo hago un reporte?',
                '¿Qué nivel de urgencia elegir?',
                '¿Cómo seguir mi reporte?',
                '¿Qué fotos subir?'
            ]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/estadisticas_ia')
def estadisticas_ia():
    """Página con estadísticas generadas por IA"""
    try:
        # Obtener reportes para análisis
        reportes = ReporteCiudadano.query.all()
        
        # Análisis mock con IA
        analisis = {
            'total_reportes': len(reportes),
            'tipos_frecuentes': [
                {'tipo': 'Basura y Residuos', 'cantidad': 12, 'porcentaje': 45},
                {'tipo': 'Problemas Hídricos', 'cantidad': 8, 'porcentaje': 30},
                {'tipo': 'Otros', 'cantidad': 7, 'porcentaje': 25}
            ],
            'zonas_criticas': [
                {'zona': 'Centro', 'reportes': 8},
                {'zona': 'Av. Independencia', 'reportes': 5},
                {'zona': 'Plaza San Martín', 'reportes': 4}
            ],
            'tendencias': {
                'mes_actual': 15,
                'mes_anterior': 12,
                'crecimiento': '+25%'
            },
            'recomendaciones_ia': [
                'Se detecta aumento de reportes de basura en zona centro',
                'Recomendación: reforzar limpieza en Plaza San Martín',
                'Patrón detectado: más reportes los fines de semana'
            ]
        }
        
        return render_template('ciudadano/estadisticas_ia.html', analisis=analisis)
    except:
        return render_template('estadisticas_ia.html', analisis=analisis)

