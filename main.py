from datetime import date
from typing import Literal, Optional
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from servicios import ParqueaderoService

app = FastAPI(
    title="Autos Colombia · Administración del Parqueadero",
    description="Gestión de usuarios, vehículos, mensualidades, celdas y control de acceso.",
    version="2.0.0"
)

servicio = ParqueaderoService()

def render_navbar(activa: str):
    def estilo_tab(nombre_tab: str):
        if activa == nombre_tab:
            return "text-blue-600 font-semibold border-b-2 border-blue-600 h-full flex items-center"
        return "hover:text-slate-800 transition h-full flex items-center"

    return f"""
    <header class="bg-white border-b border-slate-200 px-8 h-16 flex items-center justify-between sticky top-0 z-10">
      <div class="flex items-center space-x-10 h-full">
        <a href="/" class="text-xl font-bold tracking-tight">
          <span class="text-slate-900">Autos</span><span class="text-blue-600">Colombia</span>
        </a>
        <nav class="hidden md:flex space-x-8 h-full items-center text-sm font-medium text-slate-500">
          <a href="/entrada-vista" class="{estilo_tab('entrada')}">Registro de entrada</a>
          <a href="/salida-vista" class="{estilo_tab('salida')}">Salida y ocupación</a>
          <a href="/" class="{estilo_tab('usuarios')}">Usuarios y vehículos</a>
          <a href="/celdas-vista" class="{estilo_tab('celdas')}">Celdas</a>
        </nav>
      </div>
      <div class="flex items-center space-x-4">
        <a href="/docs" target="_blank" class="text-xs font-medium text-blue-600 bg-blue-50 hover:bg-blue-100 px-3 py-1.5 rounded-lg transition">API Docs</a>
        <div class="flex items-center space-x-3 border-l border-slate-200 pl-4">
          <div class="text-right">
            <p class="text-sm font-semibold text-slate-800 leading-none">María García</p>
            <p class="text-xs text-slate-400 mt-1">Administradora</p>
          </div>
        </div>
      </div>
    </header>
    """

# =========================================================================
# VISTA 1: REGISTRO DE ENTRADA (http://127.0.0.1:8000/entrada-vista)
# =========================================================================

@app.get("/entrada-vista", response_class=HTMLResponse, include_in_schema=False)
def interfaz_entrada():
    return f"""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <title>Autos Colombia · Registro de entrada</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>body {{ font-family: 'Inter', sans-serif; background-color: #F4F7FA; color: #1E293B; }}</style>
</head>
<body class="min-h-screen flex flex-col justify-between">
  {render_navbar('entrada')}

  <main class="max-w-7xl w-full mx-auto px-6 py-8 flex-grow">
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-7">
      <div>
        <p class="text-[11px] font-semibold tracking-wider text-slate-400 uppercase">CONTROL DE ACCESO</p>
        <h1 class="text-2xl font-bold text-slate-900 mt-0.5">Registro de entrada</h1>
        <p class="text-sm text-slate-500 mt-1">Selecciona un vehículo registrado y asígnale una celda disponible compatible.</p>
      </div>
      <span class="mt-4 sm:mt-0 inline-flex items-center px-3.5 py-1.5 rounded-lg border border-slate-200 bg-white text-xs font-medium text-slate-600 shadow-sm">
        Sede principal
      </span>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
      <div class="lg:col-span-4 bg-white rounded-xl border border-slate-200/80 shadow-sm p-6">
        <h2 class="text-base font-bold text-slate-900">Asignar Celda e Ingreso</h2>
        <p class="text-xs text-slate-400 mt-0.5 mb-5">El sistema valida vigencia, doble ingreso y tipo de celda.</p>

        <form id="formEntrada" class="space-y-4">
          <div>
            <label class="block text-xs font-medium text-slate-700 mb-1">Vehículo registrado</label>
            <select id="selectPlaca" required
              class="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600">
              <option value="">Cargando vehículos...</option>
            </select>
          </div>

          <div>
            <label class="block text-xs font-medium text-slate-700 mb-1">Celda disponible asignada</label>
            <select id="selectCelda" required
              class="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600">
              <option value="">Cargando celdas...</option>
            </select>
          </div>

          <div id="alertaEntrada" class="hidden text-xs p-2.5 rounded-lg"></div>

          <button type="submit"
            class="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium text-sm py-2.5 px-4 rounded-lg shadow-sm transition cursor-pointer">
            Asignar Celda y Registrar Entrada
          </button>
        </form>
      </div>

      <div class="lg:col-span-8 bg-white rounded-xl border border-slate-200/80 shadow-sm p-6">
        <div class="flex items-start justify-between mb-4">
          <div>
            <h2 class="text-base font-bold text-slate-900">Vehículos Actualmente en el Parqueadero</h2>
            <p class="text-xs text-slate-400 mt-0.5">Celdas ocupadas y registros activos en tiempo real.</p>
          </div>
          <span id="badgeActivos" class="px-2.5 py-1 text-xs font-semibold text-blue-600 bg-blue-50 rounded-full">0 activos</span>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="border-b border-slate-100 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                <th class="py-3 px-2">ID</th>
                <th class="py-3 px-2">Placa</th>
                <th class="py-3 px-2">Propietario</th>
                <th class="py-3 px-2">Tipo</th>
                <th class="py-3 px-2">Celda</th>
                <th class="py-3 px-2">Hora Ingreso</th>
                <th class="py-3 px-2">Estado</th>
              </tr>
            </thead>
            <tbody id="tablaActivos" class="divide-y divide-slate-100 text-xs"></tbody>
          </table>
        </div>
      </div>
    </div>
  </main>

  <footer class="max-w-7xl w-full mx-auto px-6 py-5 flex justify-between text-xs text-slate-400">
    <p>© 2026 Autos Colombia</p>
    <p>Control de ingreso validado</p>
  </footer>

  <script>
    async function cargarDatosEntrada() {{
      const [resOcup, resActivos, resVeh] = await Promise.all([
        fetch('/ocupacion'),
        fetch('/ingresos-activos'),
        fetch('/usuarios-vehiculos')
      ]);
      const dataOcup = await resOcup.json();
      const dataActivos = await resActivos.json();
      const dataVeh = await resVeh.json();

      const selectPlaca = document.getElementById('selectPlaca');
      const vehiculos = (dataVeh.registros || []).filter(v => v.Placa);
      selectPlaca.innerHTML = vehiculos.length
        ? vehiculos.map(v => `<option value="${{v.Placa}}">${{v.Placa}} · ${{v.Propietario}} (${{v.Tipo}} - ${{v.Estado}})</option>`).join('')
        : '<option value="">No hay vehículos registrados</option>';

      const selectCelda = document.getElementById('selectCelda');
      const disponibles = (dataOcup.celdas || []).filter(c => c.estado === 'DISPONIBLE');
      selectCelda.innerHTML = disponibles.length
        ? disponibles.map(c => `<option value="${{c.id_celda}}">${{c.numero_celda}} (${{c.tipo_vehiculo}})</option>`).join('')
        : '<option value="">No hay celdas disponibles</option>';

      const tbody = document.getElementById('tablaActivos');
      const registros = dataActivos.registros || [];
      document.getElementById('badgeActivos').innerText = `${{registros.length}} activos`;

      tbody.innerHTML = registros.length ? registros.map(r => `
        <tr class="hover:bg-slate-50/70">
          <td class="py-3 px-2 text-slate-400">#${{r.id_registro}}</td>
          <td class="py-3 px-2"><span class="px-2 py-0.5 bg-slate-100 border border-slate-200 rounded font-semibold text-slate-700">${{r.placa}}</span></td>
          <td class="py-3 px-2 font-medium text-slate-800">${{r.propietario}}</td>
          <td class="py-3 px-2 text-slate-600">${{r.tipo_vehiculo === 'CARRO' ? '🚗 Carro' : '🏍️ Moto'}}</td>
          <td class="py-3 px-2 font-semibold text-blue-600">${{r.numero_celda}}</td>
          <td class="py-3 px-2 text-slate-500">${{r.fecha_hora_ingreso}}</td>
          <td class="py-3 px-2"><span class="px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-emerald-50 text-emerald-600">En parqueadero</span></td>
        </tr>
      `).join('') : '<tr><td colspan="7" class="py-6 text-center text-slate-400">No hay vehículos dentro del parqueadero.</td></tr>';
    }}

    document.getElementById('formEntrada').addEventListener('submit', async (e) => {{
      e.preventDefault();
      const alerta = document.getElementById('alertaEntrada');
      const params = new URLSearchParams({{
        placa: document.getElementById('selectPlaca').value,
        id_celda: document.getElementById('selectCelda').value
      }});
      const res = await fetch(`/ingreso?${{params.toString()}}`, {{ method: 'POST' }});
      const data = await res.json();

      alerta.className = data.exito
        ? 'text-xs p-2.5 rounded-lg bg-emerald-50 text-emerald-700 border border-emerald-200'
        : 'text-xs p-2.5 rounded-lg bg-rose-50 text-rose-600 border border-rose-200';
      alerta.innerText = data.mensaje;
      alerta.classList.remove('hidden');

      if (data.exito) {{
        cargarDatosEntrada();
      }}
    }});

    cargarDatosEntrada();
  </script>
</body>
</html>
"""

# =========================================================================
# VISTA 2: SALIDA Y OCUPACIÓN (http://127.0.0.1:8000/salida-vista)
# =========================================================================

@app.get("/salida-vista", response_class=HTMLResponse, include_in_schema=False)
def interfaz_salida():
    return f"""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <title>Autos Colombia · Salida y ocupación</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>body {{ font-family: 'Inter', sans-serif; background-color: #F4F7FA; color: #1E293B; }}</style>
</head>
<body class="min-h-screen flex flex-col justify-between">
  {render_navbar('salida')}

  <main class="max-w-7xl w-full mx-auto px-6 py-8 flex-grow space-y-6">
    <div>
      <p class="text-[11px] font-semibold tracking-wider text-slate-400 uppercase">OPERACIÓN EN TIEMPO REAL</p>
      <h1 class="text-2xl font-bold text-slate-900 mt-0.5">Salida y ocupación</h1>
      <p class="text-sm text-slate-500 mt-1">Registra la salida de vehículos y libera las celdas automáticamente.</p>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div class="bg-white rounded-xl border border-slate-200/80 p-5 shadow-sm">
        <p class="text-xs font-medium text-slate-400">Total de Celdas</p>
        <p id="kpiTotal" class="text-2xl font-bold text-slate-900 mt-1">0</p>
      </div>
      <div class="bg-white rounded-xl border border-slate-200/80 p-5 shadow-sm">
        <p class="text-xs font-medium text-emerald-600">Celdas Disponibles</p>
        <p id="kpiDisponibles" class="text-2xl font-bold text-emerald-600 mt-1">0</p>
      </div>
      <div class="bg-white rounded-xl border border-slate-200/80 p-5 shadow-sm">
        <p class="text-xs font-medium text-rose-600">Celdas Ocupadas</p>
        <p id="kpiOcupadas" class="text-2xl font-bold text-rose-600 mt-1">0</p>
      </div>
    </div>

    <div id="alertaSalida" class="hidden text-xs p-3 rounded-lg"></div>

    <div class="bg-white rounded-xl border border-slate-200/80 shadow-sm p-6">
      <h2 class="text-base font-bold text-slate-900">Vehículos Activos Pendientes de Salida</h2>
      <p class="text-xs text-slate-400 mt-0.5 mb-5">Haz clic en "Registrar Salida" para finalizar el turno y liberar la celda.</p>

      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="border-b border-slate-100 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
              <th class="py-3 px-2">ID Registro</th>
              <th class="py-3 px-2">Placa</th>
              <th class="py-3 px-2">Propietario</th>
              <th class="py-3 px-2">Tipo</th>
              <th class="py-3 px-2">Celda Ocupada</th>
              <th class="py-3 px-2">Ingreso</th>
              <th class="py-3 px-2 text-right">Acción</th>
            </tr>
          </thead>
          <tbody id="tablaSalidas" class="divide-y divide-slate-100 text-xs"></tbody>
        </table>
      </div>
    </div>
  </main>

  <footer class="max-w-7xl w-full mx-auto px-6 py-5 flex justify-between text-xs text-slate-400">
    <p>© 2026 Autos Colombia</p>
    <p>Control de salida y disponibilidad</p>
  </footer>

  <script>
    async function cargarSalidaYOcupacion() {{
      const [resOcup, resActivos] = await Promise.all([
        fetch('/ocupacion'),
        fetch('/ingresos-activos')
      ]);
      const dataOcup = await resOcup.json();
      const dataActivos = await resActivos.json();

      document.getElementById('kpiTotal').innerText = dataOcup.total_celdas;
      document.getElementById('kpiDisponibles').innerText = dataOcup.disponibles;
      document.getElementById('kpiOcupadas').innerText = dataOcup.ocupadas;

      const tbody = document.getElementById('tablaSalidas');
      const registros = dataActivos.registros || [];

      if (!registros.length) {{
        tbody.innerHTML = '<tr><td colspan="7" class="py-6 text-center text-slate-400">No hay vehículos dentro del parqueadero en este momento.</td></tr>';
        return;
      }}

      tbody.innerHTML = registros.map(r => `
        <tr class="hover:bg-slate-50/70">
          <td class="py-3.5 px-2 font-semibold text-slate-500">#${{r.id_registro}}</td>
          <td class="py-3.5 px-2"><span class="px-2 py-0.5 bg-slate-100 border border-slate-200 rounded font-semibold text-slate-700">${{r.placa}}</span></td>
          <td class="py-3.5 px-2 font-medium text-slate-800">${{r.propietario}}</td>
          <td class="py-3.5 px-2 text-slate-600">${{r.tipo_vehiculo === 'CARRO' ? '🚗 Carro' : '🏍️ Moto'}}</td>
          <td class="py-3.5 px-2 font-bold text-rose-600">${{r.numero_celda}}</td>
          <td class="py-3.5 px-2 text-slate-500">${{r.fecha_hora_ingreso}}</td>
          <td class="py-3.5 px-2 text-right">
            <button onclick="procesarSalida(${{r.id_registro}})"
              class="bg-blue-600 hover:bg-blue-700 text-white font-medium text-xs px-3.5 py-1.5 rounded-lg transition cursor-pointer">
              Registrar Salida
            </button>
          </td>
        </tr>
      `).join('');
    }}

    async function procesarSalida(idRegistro) {{
      const res = await fetch(`/salida?id_registro=${{idRegistro}}`, {{ method: 'POST' }});
      const data = await res.json();
      const alerta = document.getElementById('alertaSalida');

      alerta.className = data.exito
        ? 'text-xs p-3 rounded-lg bg-emerald-50 text-emerald-700 border border-emerald-200'
        : 'text-xs p-3 rounded-lg bg-rose-50 text-rose-600 border border-rose-200';
      alerta.innerText = data.mensaje;
      alerta.classList.remove('hidden');
      cargarSalidaYOcupacion();
    }}

    cargarSalidaYOcupacion();
  </script>
</body>
</html>
"""

# =========================================================================
# VISTA 3: USUARIOS Y VEHÍCULOS (http://127.0.0.1:8000/)
# =========================================================================

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def interfaz_usuarios():
    return f"""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Autos Colombia · Usuarios y vehículos</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>body {{ font-family: 'Inter', sans-serif; background-color: #F4F7FA; color: #1E293B; }}</style>
</head>
<body class="min-h-screen flex flex-col justify-between">
  {render_navbar('usuarios')}

  <main class="max-w-7xl w-full mx-auto px-6 py-8 flex-grow">
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-7">
      <div>
        <p class="text-[11px] font-semibold tracking-wider text-slate-400 uppercase">ADMINISTRACIÓN DEL PARQUEADERO</p>
        <h1 class="text-2xl font-bold text-slate-900 mt-0.5">Usuarios y vehículos</h1>
        <p class="text-sm text-slate-500 mt-1">Registra usuarios, asígnales celda disponible, activa/desactiva mensualidades o elimina registros.</p>
      </div>
      <div class="mt-4 sm:mt-0">
        <span class="inline-flex items-center px-3.5 py-1.5 rounded-lg border border-slate-200 bg-white text-xs font-medium text-slate-600 shadow-sm">
          Sede principal
        </span>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
      <div class="lg:col-span-4 bg-white rounded-xl border border-slate-200/80 shadow-sm p-6">
        <h2 class="text-base font-bold text-slate-900">Registrar Usuario y Vehículo</h2>
        <p class="text-xs text-slate-400 mt-0.5 mb-5">Completa los datos y elige si deseas asignarle una celda de una vez.</p>

        <form id="registroForm" class="space-y-3.5">
          <div>
            <label class="block text-xs font-medium text-slate-700 mb-1">Nombre completo</label>
            <input type="text" id="nombre" required placeholder="Ej. Carlos Rodríguez"
              class="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 placeholder:text-slate-300" />
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-700 mb-1">Documento de identidad</label>
            <input type="text" id="documento" required placeholder="Ej. 1.023.456.789"
              class="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 placeholder:text-slate-300" />
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-700 mb-1">Teléfono</label>
            <input type="text" id="telefono" placeholder="Ej. 300 123 4567"
              class="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 placeholder:text-slate-300" />
          </div>

          <div class="pt-3 border-t border-slate-100">
            <h3 class="text-xs font-bold text-slate-800 mb-3">Datos del Vehículo y Mensualidad</h3>
            <div class="grid grid-cols-2 gap-3 mb-3">
              <div>
                <label class="block text-xs font-medium text-slate-700 mb-1">Placa</label>
                <input type="text" id="placa" required placeholder="Ej. ABC-999"
                  class="w-full px-3 py-2 text-sm uppercase border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 placeholder:text-slate-300" />
              </div>
              <div>
                <label class="block text-xs font-medium text-slate-700 mb-1">Tipo de vehículo</label>
                <select id="tipo_vehiculo"
                  class="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600">
                  <option value="CARRO">Carro</option>
                  <option value="MOTO">Moto</option>
                </select>
              </div>
            </div>

            <div class="mb-3">
              <label class="block text-xs font-medium text-slate-700 mb-1">Estado mensualidad</label>
              <select id="estado_mensualidad"
                class="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600">
                <option value="ACTIVO">Activo</option>
                <option value="INACTIVO">Inactivo</option>
              </select>
            </div>

            <div class="grid grid-cols-2 gap-3 mb-3">
              <div>
                <label class="block text-xs font-medium text-slate-700 mb-1">Fecha inicio</label>
                <input type="date" id="fecha_inicio" required
                  class="w-full px-2.5 py-2 text-xs border border-slate-200 rounded-lg text-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600" />
              </div>
              <div>
                <label class="block text-xs font-medium text-slate-700 mb-1">Fecha fin</label>
                <input type="date" id="fecha_fin" required
                  class="w-full px-2.5 py-2 text-xs border border-slate-200 rounded-lg text-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600" />
              </div>
            </div>

            <div>
              <label class="block text-xs font-medium text-slate-700 mb-1">Asignar celda disponible (opcional)</label>
              <select id="celda_inicial"
                class="w-full px-3 py-2 text-xs border border-slate-200 rounded-lg bg-white text-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600">
                <option value="">No asignar celda ahora (solo registrar)</option>
              </select>
            </div>
          </div>

          <div id="alertaMensaje" class="hidden text-xs p-2.5 rounded-lg"></div>

          <button type="submit"
            class="w-full mt-2 bg-blue-600 hover:bg-blue-700 text-white font-medium text-sm py-2.5 px-4 rounded-lg shadow-sm flex items-center justify-center space-x-2 transition cursor-pointer">
            <span>Guardar Usuario y Vehículo</span>
          </button>
        </form>
      </div>

      <div class="lg:col-span-8 bg-white rounded-xl border border-slate-200/80 shadow-sm p-6">
        <div class="flex items-start justify-between">
          <div>
            <h2 class="text-base font-bold text-slate-900">Usuarios y Vehículos Registrados</h2>
            <p class="text-xs text-slate-400 mt-0.5">Activa o desactiva mensualidades o elimina usuarios desde la tabla.</p>
          </div>
          <span id="contadorUsuarios" class="px-2.5 py-1 text-xs font-semibold text-blue-600 bg-blue-50 rounded-full">0 usuarios</span>
        </div>

        <div id="alertaTabla" class="hidden mt-3 text-xs p-2.5 rounded-lg"></div>

        <div class="relative mt-4 mb-5">
          <input type="text" id="buscador" onkeyup="filtrarTabla()" placeholder="Buscar por placa o documento..."
            class="w-full pl-4 pr-4 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 placeholder:text-slate-400" />
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="border-b border-slate-100 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                <th class="py-3 px-2">Propietario</th>
                <th class="py-3 px-2">Documento</th>
                <th class="py-3 px-2">Placa</th>
                <th class="py-3 px-2">Tipo</th>
                <th class="py-3 px-2">Vigencia</th>
                <th class="py-3 px-2">Estado</th>
                <th class="py-3 px-2 text-right">Acciones</th>
              </tr>
            </thead>
            <tbody id="tablaCuerpo" class="divide-y divide-slate-100 text-xs"></tbody>
          </table>
        </div>

        <div class="flex items-center justify-between pt-4 mt-2 border-t border-slate-100 text-xs text-slate-400">
          <span id="textoPaginacion">Mostrando 0 registros</span>
        </div>
      </div>
    </div>
  </main>

  <footer class="max-w-7xl w-full mx-auto px-6 py-5 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-400">
    <p>© 2026 Autos Colombia</p>
    <p>Gestión de parqueaderos, sin complicaciones.</p>
  </footer>

  <script>
    let registrosGlobales = [];
    function formatearFecha(fechaStr) {{
      if (!fechaStr || fechaStr === 'None') return '';
      const meses = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'];
      const partes = fechaStr.split('-');
      return `${{partes[2]}} ${{meses[parseInt(partes[1], 10) - 1]}}`;
    }}
    async function cargarCeldasDisponiblesSelect() {{
      const res = await fetch('/ocupacion');
      const data = await res.json();
      const disponibles = (data.celdas || []).filter(c => c.estado === 'DISPONIBLE');
      const select = document.getElementById('celda_inicial');
      select.innerHTML = '<option value="">No asignar celda ahora (solo registrar)</option>' +
        disponibles.map(c => `<option value="${{c.id_celda}}">Asignar celda ${{c.numero_celda}} (${{c.tipo_vehiculo}})</option>`).join('');
    }}
    async function cargarUsuarios() {{
      const res = await fetch('/usuarios-vehiculos');
      const data = await res.json();
      registrosGlobales = data.registros || [];
      renderizarTabla(registrosGlobales);
      cargarCeldasDisponiblesSelect();
    }}
    async function cambiarEstadoMensualidad(placa, nuevoEstado) {{
      const res = await fetch(`/vehiculos/${{placa}}/estado?nuevo_estado=${{nuevoEstado}}`, {{ method: 'PATCH' }});
      const data = await res.json();
      mostrarAlertaTabla(data);
      cargarUsuarios();
    }}
    async function borrarUsuario(idUsuario, nombre) {{
      const res = await fetch(`/usuarios/${{idUsuario}}`, {{ method: 'DELETE' }});
      const data = await res.json();
      mostrarAlertaTabla(data);
      cargarUsuarios();
    }}
    function mostrarAlertaTabla(data) {{
      const alerta = document.getElementById('alertaTabla');
      alerta.className = data.exito
        ? 'mt-3 text-xs p-2.5 rounded-lg bg-emerald-50 text-emerald-700 border border-emerald-200'
        : 'mt-3 text-xs p-2.5 rounded-lg bg-rose-50 text-rose-600 border border-rose-200';
      alerta.innerText = data.mensaje;
      alerta.classList.remove('hidden');
    }}
    function renderizarTabla(lista) {{
      const tbody = document.getElementById('tablaCuerpo');
      tbody.innerHTML = '';
      lista.forEach(item => {{
        const esActivo = item.Estado === 'ACTIVO';
        const esCarro = item.Tipo === 'CARRO';
        let vigenciaTexto = 'Sin vigencia';
        let anio = '2026';
        if (item.Vigencia && item.Vigencia.includes(' a ')) {{
          const [fIni, fFin] = item.Vigencia.split(' a ');
          vigenciaTexto = `${{formatearFecha(fIni)}} – ${{formatearFecha(fFin)}}`;
          anio = fFin.split('-')[0];
        }}
        const botonEstado = item.Placa
          ? (esActivo
              ? `<button onclick="cambiarEstadoMensualidad('${{item.Placa}}', 'INACTIVO')" class="px-2 py-1 rounded-md text-[11px] font-medium bg-amber-50 text-amber-700 hover:bg-amber-100 transition cursor-pointer">Desactivar</button>`
              : `<button onclick="cambiarEstadoMensualidad('${{item.Placa}}', 'ACTIVO')" class="px-2 py-1 rounded-md text-[11px] font-medium bg-blue-50 text-blue-600 hover:bg-blue-100 transition cursor-pointer">Activar</button>`)
          : '';
        const botonEliminar = `<button onclick="borrarUsuario(${{item.id_usuario}}, '${{item.Propietario}}')" class="px-2 py-1 rounded-md text-[11px] font-medium bg-rose-50 text-rose-600 hover:bg-rose-100 transition cursor-pointer">Eliminar</button>`;

        tbody.innerHTML += `
          <tr class="hover:bg-slate-50/70 transition">
            <td class="py-3.5 px-2 font-semibold text-slate-800">${{item.Propietario}}</td>
            <td class="py-3.5 px-2 text-slate-500">${{item.Documento}}</td>
            <td class="py-3.5 px-2"><span class="px-2 py-0.5 bg-slate-100 border border-slate-200 rounded font-semibold text-slate-700 text-[11px]">${{item.Placa || 'N/A'}}</span></td>
            <td class="py-3.5 px-2 text-slate-600">${{esCarro ? '🚗 Carro' : '🏍️ Moto'}}</td>
            <td class="py-3.5 px-2"><div class="text-slate-700 font-medium">${{vigenciaTexto}}</div><div class="text-[10px] text-slate-400">${{anio}}</div></td>
            <td class="py-3.5 px-2">${{esActivo
              ? '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-emerald-50 text-emerald-600"><span class="w-1.5 h-1.5 rounded-full bg-emerald-500 mr-1.5"></span>Activo</span>'
              : '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-rose-50 text-rose-600"><span class="w-1.5 h-1.5 rounded-full bg-rose-500 mr-1.5"></span>Inactivo</span>'
            }}</td>
            <td class="py-3.5 px-2 text-right space-x-1 whitespace-nowrap">${{botonEstado}} ${{botonEliminar}}</td>
          </tr>`;
      }});
      document.getElementById('contadorUsuarios').innerText = `${{lista.length}} usuarios`;
      document.getElementById('textoPaginacion').innerText = `Mostrando 1–${{lista.length}} de ${{lista.length}} registros`;
    }}
    function filtrarTabla() {{
      const texto = document.getElementById('buscador').value.toLowerCase();
      renderizarTabla(registrosGlobales.filter(u =>
        (u.Placa && u.Placa.toLowerCase().includes(texto)) ||
        (u.Documento && u.Documento.toLowerCase().includes(texto)) ||
        (u.Propietario && u.Propietario.toLowerCase().includes(texto))
      ));
    }}
    document.getElementById('registroForm').addEventListener('submit', async (e) => {{
      e.preventDefault();
      const alerta = document.getElementById('alertaMensaje');
      const params = new URLSearchParams({{
        nombre: document.getElementById('nombre').value.trim(),
        documento: document.getElementById('documento').value.trim(),
        telefono: document.getElementById('telefono').value.trim(),
        placa: document.getElementById('placa').value.trim().toUpperCase(),
        tipo_vehiculo: document.getElementById('tipo_vehiculo').value,
        estado_mensualidad: document.getElementById('estado_mensualidad').value,
        fecha_inicio: document.getElementById('fecha_inicio').value,
        fecha_fin: document.getElementById('fecha_fin').value
      }});
      const celdaInicial = document.getElementById('celda_inicial').value;
      if (celdaInicial) {{
        params.append('id_celda_inicial', celdaInicial);
      }}
      const res = await fetch(`/usuarios-vehiculos?${{params.toString()}}`, {{ method: 'POST' }});
      const data = await res.json();
      alerta.className = data.exito
        ? 'text-xs p-2.5 rounded-lg bg-emerald-50 text-emerald-700 border border-emerald-200'
        : 'text-xs p-2.5 rounded-lg bg-rose-50 text-rose-600 border border-rose-200';
      alerta.innerText = data.mensaje;
      alerta.classList.remove('hidden');
      if (data.exito) {{ document.getElementById('registroForm').reset(); cargarUsuarios(); }}
    }});
    cargarUsuarios();
  </script>
</body>
</html>
"""

# =========================================================================
# VISTA 4: CELDAS DE PARQUEO (http://127.0.0.1:8000/celdas-vista)
# =========================================================================

@app.get("/celdas-vista", response_class=HTMLResponse, include_in_schema=False)
def interfaz_celdas():
    return f"""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Autos Colombia · Celdas de parqueo</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>body {{ font-family: 'Inter', sans-serif; background-color: #F4F7FA; color: #1E293B; }}</style>
</head>
<body class="min-h-screen flex flex-col justify-between">
  {render_navbar('celdas')}

  <main class="max-w-7xl w-full mx-auto px-8 py-8 flex-grow space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-900">Celdas de parqueo</h1>
        <p class="text-sm text-slate-500 mt-1">Crea y administra los espacios de tu parqueadero.</p>
      </div>
      <div class="mt-4 sm:mt-0 bg-white border border-slate-200 rounded-xl px-4 py-2.5 flex items-center space-x-2.5 shadow-sm">
        <span id="totalCeldasBadge" class="text-base font-bold text-slate-900">0</span>
        <span class="text-xs text-slate-400">celdas en total</span>
      </div>
    </div>

    <div class="bg-white rounded-xl border border-slate-200/80 shadow-sm p-6">
      <h2 class="text-base font-bold text-slate-900">Crear Nueva Celda de Parqueo</h2>
      <p class="text-xs text-slate-400 mt-0.5 mb-5">Asigna un código único y selecciona el tipo de vehículo permitido.</p>

      <form id="formCelda" class="grid grid-cols-1 md:grid-cols-12 gap-4 items-end">
        <div class="md:col-span-5">
          <label class="block text-xs font-medium text-slate-700 mb-1.5">Código de celda</label>
          <input type="text" id="numero_celda" required placeholder="ej. M-202"
            class="w-full px-3.5 py-2.5 text-sm uppercase border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 placeholder:text-slate-300" />
        </div>
        <div class="md:col-span-5">
          <label class="block text-xs font-medium text-slate-700 mb-1.5">Tipo de vehículo permitido</label>
          <select id="tipo_celda"
            class="w-full px-3.5 py-2.5 text-sm border border-slate-200 rounded-lg bg-white text-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600">
            <option value="CARRO">Carro</option>
            <option value="MOTO">Moto</option>
          </select>
        </div>
        <div class="md:col-span-2">
          <button type="submit"
            class="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium text-sm py-2.5 px-4 rounded-lg shadow-sm flex items-center justify-center space-x-2 transition cursor-pointer">
            <span>+</span>
            <span>Crear Celda</span>
          </button>
        </div>
      </form>
      <div id="alertaCelda" class="hidden mt-3 text-xs p-2.5 rounded-lg"></div>
    </div>

    <div class="bg-white rounded-xl border border-slate-200/80 shadow-sm p-6">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-4 border-b border-slate-100">
        <div>
          <h2 class="text-base font-bold text-slate-900">Mapa de Celdas por Tipo de Vehículo</h2>
          <p class="text-xs text-slate-400 mt-0.5">Consulta la disponibilidad de cada espacio de parqueo.</p>
        </div>
        <div class="flex items-center space-x-5 mt-3 sm:mt-0 text-xs font-medium">
          <span class="flex items-center text-slate-600"><span class="w-2 h-2 rounded-full bg-emerald-500 mr-2"></span><span id="contadorDisponibles">0 disponibles</span></span>
          <span class="flex items-center text-slate-600"><span class="w-2 h-2 rounded-full bg-rose-500 mr-2"></span><span id="contadorOcupadas">0 ocupada</span></span>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 pt-5">
        <div>
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-xs font-bold text-slate-700">Zona Carros</h3>
            <span id="totalCarros" class="text-xs text-slate-400">0 celdas</span>
          </div>
          <div id="gridCarros" class="grid grid-cols-1 sm:grid-cols-2 gap-4"></div>
        </div>

        <div class="lg:border-l lg:border-slate-100 lg:pl-8">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-xs font-bold text-slate-700">Zona Motos</h3>
            <span id="totalMotos" class="text-xs text-slate-400">0 celdas</span>
          </div>
          <div id="gridMotos" class="grid grid-cols-1 sm:grid-cols-2 gap-4"></div>
        </div>
      </div>

      <div class="flex items-center justify-between pt-5 mt-6 border-t border-slate-100 text-[11px] text-slate-400">
        <span id="pieRegistradas">0 celdas registradas</span>
        <span>Disponibilidad por celda</span>
      </div>
    </div>
  </main>

  <footer class="max-w-7xl w-full mx-auto px-8 py-5 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-400">
    <p>Autos Colombia</p>
    <p>Gestión de Parqueaderos · Administración de celdas</p>
  </footer>

  <script>
    function crearTarjetaCelda(celda) {{
      const disponible = celda.estado === 'DISPONIBLE';
      const esCarro = celda.tipo_vehiculo === 'CARRO';
      const bordeColor = disponible ? 'border-emerald-500' : 'border-rose-500';
      const barraLateral = disponible ? 'bg-emerald-500' : 'bg-rose-500';
      const badgeClase = disponible ? 'bg-emerald-50 text-emerald-600' : 'bg-rose-50 text-rose-600';
      const puntoClase = disponible ? 'bg-emerald-500' : 'bg-rose-500';

      return `
        <div class="relative bg-white rounded-xl border ${{bordeColor}} p-4 shadow-sm overflow-hidden">
          <span class="absolute left-0 top-3 bottom-3 w-1 rounded-r ${{barraLateral}}"></span>
          <div class="flex items-center justify-between mb-3">
            <div class="w-9 h-9 rounded-lg bg-slate-100 flex items-center justify-center text-lg">${{esCarro ? '🚗' : '🏍️'}}</div>
            <span class="text-xs text-slate-400 font-medium">${{esCarro ? 'Carro' : 'Moto'}}</span>
          </div>
          <div class="text-xl font-bold text-slate-900 mb-3">${{celda.numero_celda}}</div>
          <div class="flex items-center justify-between">
            <span class="inline-flex items-center px-2.5 py-1 rounded-md text-[11px] font-semibold ${{badgeClase}}">
              <span class="w-1.5 h-1.5 rounded-full ${{puntoClase}} mr-1.5"></span>
              ${{disponible ? 'Disponible' : 'Ocupada'}}
            </span>
            ${{disponible ? `<button onclick="borrarCelda(${{celda.id_celda}})" class="text-[11px] text-slate-400 hover:text-rose-600 transition cursor-pointer">Eliminar</button>` : ''}}
          </div>
        </div>`;
    }}

    async function borrarCelda(idCelda) {{
      const res = await fetch(`/celdas/${{idCelda}}`, {{ method: 'DELETE' }});
      const data = await res.json();
      const alerta = document.getElementById('alertaCelda');
      alerta.className = data.exito
        ? 'mt-3 text-xs p-2.5 rounded-lg bg-emerald-50 text-emerald-700 border border-emerald-200'
        : 'mt-3 text-xs p-2.5 rounded-lg bg-rose-50 text-rose-600 border border-rose-200';
      alerta.innerText = data.mensaje;
      alerta.classList.remove('hidden');
      cargarCeldas();
    }}

    async function cargarCeldas() {{
      const res = await fetch('/ocupacion');
      const data = await res.json();
      const celdas = data.celdas || [];
      const carros = celdas.filter(c => c.tipo_vehiculo === 'CARRO');
      const motos = celdas.filter(c => c.tipo_vehiculo === 'MOTO');

      document.getElementById('gridCarros').innerHTML = carros.map(crearTarjetaCelda).join('');
      document.getElementById('gridMotos').innerHTML = motos.map(crearTarjetaCelda).join('');
      document.getElementById('totalCeldasBadge').innerText = data.total_celdas;
      document.getElementById('contadorDisponibles').innerText = `${{data.disponibles}} disponibles`;
      document.getElementById('contadorOcupadas').innerText = `${{data.ocupadas}} ${{data.ocupadas === 1 ? 'ocupada' : 'ocupadas'}}`;
      document.getElementById('totalCarros').innerText = `${{carros.length}} celdas`;
      document.getElementById('totalMotos').innerText = `${{motos.length}} celdas`;
      document.getElementById('pieRegistradas').innerText = `${{data.total_celdas}} celdas registradas`;
    }}

    document.getElementById('formCelda').addEventListener('submit', async (e) => {{
      e.preventDefault();
      const alerta = document.getElementById('alertaCelda');
      const params = new URLSearchParams({{
        numero_celda: document.getElementById('numero_celda').value.trim().toUpperCase(),
        tipo_vehiculo: document.getElementById('tipo_celda').value
      }});
      const res = await fetch(`/celdas?${{params.toString()}}`, {{ method: 'POST' }});
      const data = await res.json();
      alerta.className = data.exito
        ? 'mt-3 text-xs p-2.5 rounded-lg bg-emerald-50 text-emerald-700 border border-emerald-200'
        : 'mt-3 text-xs p-2.5 rounded-lg bg-rose-50 text-rose-600 border border-rose-200';
      alerta.innerText = data.mensaje;
      alerta.classList.remove('hidden');
      if (data.exito) {{ document.getElementById('formCelda').reset(); cargarCeldas(); }}
    }});

    cargarCeldas();
  </script>
</body>
</html>
"""

# =========================================================================
# ENDPOINTS API REST (BACKEND + SWAGGER /docs)
# =========================================================================

@app.post("/usuarios-vehiculos", tags=["Usuarios y vehículos"], summary="Registrar Usuario y Vehículo")
def registrar_usuario_y_vehiculo(
    nombre: str = Query(..., description="Nombre completo (Ej. Carlos Rodríguez)"),
    documento: str = Query(..., description="Documento de identidad (Ej. 1.023.456.789)"),
    telefono: str = Query(..., description="Teléfono (Ej. 300 123 4567)"),
    placa: str = Query(..., description="Placa (Ej. ABC-999)"),
    tipo_vehiculo: Literal["CARRO", "MOTO"] = Query("CARRO", description="Tipo de vehículo"),
    estado_mensualidad: Literal["ACTIVO", "INACTIVO"] = Query("ACTIVO", description="Estado mensualidad"),
    fecha_inicio: date = Query(..., description="Fecha inicio (AAAA-MM-DD)"),
    fecha_fin: date = Query(..., description="Fecha fin (AAAA-MM-DD)"),
    id_celda_inicial: Optional[int] = Query(None, description="ID de celda disponible opcional para asignar de inmediato")
):
    return servicio.registrar_usuario_y_vehiculo(
        nombre, documento, telefono, placa,
        tipo_vehiculo, estado_mensualidad, fecha_inicio, fecha_fin, id_celda_inicial
    )

@app.get("/usuarios-vehiculos", tags=["Usuarios y vehículos"], summary="Usuarios y Vehículos Registrados")
def consultar_usuarios_y_vehiculos(
    buscar: Optional[str] = Query(None, description="Buscar por placa o documento...")
):
    return servicio.listar_usuarios_y_vehiculos(buscar)

@app.patch("/vehiculos/{placa}/estado", tags=["Usuarios y vehículos"], summary="Activar o Desactivar Mensualidad")
def actualizar_estado_mensualidad(
    placa: str,
    nuevo_estado: Literal["ACTIVO", "INACTIVO"] = Query(..., description="Nuevo estado de mensualidad"),
    fecha_inicio: Optional[date] = Query(None, description="Nueva fecha inicio opcional"),
    fecha_fin: Optional[date] = Query(None, description="Nueva fecha fin opcional")
):
    return servicio.cambiar_estado_mensualidad(placa, nuevo_estado, fecha_inicio, fecha_fin)

@app.delete("/usuarios/{id_usuario}", tags=["Usuarios y vehículos"], summary="Eliminar Usuario")
def eliminar_usuario(id_usuario: int):
    return servicio.eliminar_usuario(id_usuario)

@app.post("/celdas", tags=["Celdas"], summary="Crear Nueva Celda")
def crear_celda(
    numero_celda: str = Query(..., description="Código de celda (Ej. C-103 o M-202)"),
    tipo_vehiculo: Literal["CARRO", "MOTO"] = Query("CARRO", description="Tipo de vehículo permitido")
):
    return servicio.crear_celda(numero_celda, tipo_vehiculo)

@app.delete("/celdas/{id_celda}", tags=["Celdas"], summary="Eliminar Celda Disponible")
def eliminar_celda(id_celda: int):
    return servicio.eliminar_celda(id_celda)

@app.get("/ocupacion", tags=["Celdas"], summary="Consultar Ocupación de Celdas")
def consultar_ocupacion():
    return servicio.consultar_ocupacion()

@app.get("/ingresos-activos", tags=["Registro de entrada y salida"], summary="Listar Vehículos en el Parqueadero")
def consultar_ingresos_activos():
    return servicio.listar_ingresos_activos()

@app.post("/ingreso", tags=["Registro de entrada y salida"], summary="Registrar Entrada de Vehículo")
def registrar_ingreso(
    placa: str = Query(..., description="Placa del vehículo"),
    id_celda: int = Query(..., description="ID de la celda asignada")
):
    return servicio.registrar_ingreso(placa, id_celda)

@app.post("/salida", tags=["Registro de entrada y salida"], summary="Registrar Salida de Vehículo")
def registrar_salida(
    id_registro: int = Query(..., description="ID del registro activo")
):
    return servicio.registrar_salida(id_registro)