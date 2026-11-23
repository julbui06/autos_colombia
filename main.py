from datetime import date
from typing import Literal, Optional
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from servicios import ParqueaderoService

app = FastAPI(
    title="Autos Colombia · Sistema Integral de Parqueadero",
    description="Iteraciones 1, 2 y 3: Control de acceso, cuentas/roles, propietarios, celdas y gestión de pagos.",
    version="3.1.0"
)

servicio = ParqueaderoService()

def render_navbar(activa: str):
    def estilo_tab(nombre_tab: str):
        if activa == nombre_tab:
            return "text-blue-600 font-semibold border-b-2 border-blue-600 h-full flex items-center"
        return "hover:text-slate-800 transition h-full flex items-center"

    return f"""
    <header class="bg-white border-b border-slate-200 px-8 h-16 flex items-center justify-between sticky top-0 z-10">
      <div class="flex items-center space-x-8 h-full">
        <a href="/" class="text-xl font-bold tracking-tight">
          <span class="text-slate-900">Autos</span><span class="text-blue-600">Colombia</span>
        </a>
        <nav class="hidden lg:flex space-x-6 h-full items-center text-sm font-medium text-slate-500">
          <a href="/entrada-vista" class="{estilo_tab('entrada')}">Registro de entrada</a>
          <a href="/salida-vista" class="{estilo_tab('salida')}">Salida y ocupación</a>
          <a href="/" class="{estilo_tab('usuarios')}">Propietarios y vehículos</a>
          <a href="/celdas-vista" class="{estilo_tab('celdas')}">Celdas</a>
          <a href="/pagos-vista" class="{estilo_tab('pagos')}">Pagos</a>
          <a href="/cuentas-vista" class="{estilo_tab('cuentas')}">Usuarios y roles</a>
        </nav>
      </div>
      <div class="flex items-center space-x-4">
        <a href="/docs" target="_blank" class="text-xs font-medium text-blue-600 bg-blue-50 hover:bg-blue-100 px-3 py-1.5 rounded-lg transition">API Docs</a>
        <div class="flex items-center space-x-3 border-l border-slate-200 pl-4">
          <div class="text-right">
            <p id="navUserNombre" class="text-sm font-semibold text-slate-800 leading-none">María García</p>
            <p id="navUserRol" class="text-xs text-blue-600 font-medium mt-1">ADMINISTRADOR</p>
          </div>
          <a href="/login" onclick="localStorage.removeItem('autos_user')" class="text-xs text-slate-400 hover:text-rose-600 ml-2">Salir</a>
        </div>
      </div>
    </header>
    <script>
      (function() {{
        const u = JSON.parse(localStorage.getItem('autos_user') || 'null');
        if (!u && window.location.pathname !== '/login') {{
          window.location.href = '/login';
          return;
        }}
        if (u) {{
          document.getElementById('navUserNombre').innerText = u.nombre;
          document.getElementById('navUserRol').innerText = u.rol;
        }}
      }})();
    </script>
    """

# =========================================================================
# VISTA 0: LOGIN Y CONTROL DE ROLES (/login)
# =========================================================================

@app.get("/login", response_class=HTMLResponse, include_in_schema=False)
def interfaz_login():
    return """
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <title>Autos Colombia · Iniciar Sesión</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>body { font-family: 'Inter', sans-serif; background-color: #F4F7FA; color: #1E293B; }</style>
</head>
<body class="min-h-screen flex items-center justify-center p-4">
  <div class="max-w-md w-full bg-white rounded-2xl border border-slate-200 shadow-sm p-8">
    <div class="text-center mb-6">
      <div class="text-2xl font-bold tracking-tight"><span class="text-slate-900">Autos</span><span class="text-blue-600">Colombia</span></div>
      <p class="text-xs text-slate-400 mt-1">Control de Acceso y Roles del Sistema</p>
    </div>

    <form id="formLogin" class="space-y-4">
      <div>
        <label class="block text-xs font-medium text-slate-700 mb-1">Correo institucional</label>
        <input type="email" id="correo" required value="admin@autoscolombia.com"
          class="w-full px-3.5 py-2.5 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-blue-600" />
      </div>
      <div>
        <label class="block text-xs font-medium text-slate-700 mb-1">Contraseña</label>
        <input type="password" id="password" required value="admin123"
          class="w-full px-3.5 py-2.5 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-blue-600" />
      </div>
      <div id="alertaLogin" class="hidden text-xs p-2.5 rounded-lg"></div>
      <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium text-sm py-2.5 rounded-lg transition cursor-pointer">
        Ingresar al Sistema
      </button>
    </form>

    <div class="mt-6 pt-4 border-t border-slate-100 text-[11px] text-slate-500 space-y-1">
      <p class="font-semibold text-slate-700">Cuentas de prueba habilitadas:</p>
      <p>• <strong>Administrador:</strong> admin@autoscolombia.com / admin123</p>
      <p>• <strong>Operador:</strong> operador@autoscolombia.com / oper123</p>
    </div>
  </div>

  <script>
    document.getElementById('formLogin').addEventListener('submit', async (e) => {
      e.preventDefault();
      const params = new URLSearchParams({
        correo: document.getElementById('correo').value,
        password: document.getElementById('password').value
      });
      const res = await fetch(`/auth/login?${params.toString()}`, { method: 'POST' });
      const data = await res.json();
      const alerta = document.getElementById('alertaLogin');
      if (data.exito) {
        localStorage.setItem('autos_user', JSON.stringify(data.usuario));
        window.location.href = data.usuario.rol === 'ADMINISTRADOR' ? '/pagos-vista' : '/entrada-vista';
      } else {
        alerta.className = 'text-xs p-2.5 rounded-lg bg-rose-50 text-rose-600 border border-rose-200';
        alerta.innerText = data.mensaje;
        alerta.classList.remove('hidden');
      }
    });
  </script>
</body>
</html>
"""

# =========================================================================
# VISTA 6: GESTIÓN DE CUENTAS Y ROLES (/cuentas-vista)
# =========================================================================

@app.get("/cuentas-vista", response_class=HTMLResponse, include_in_schema=False)
def interfaz_cuentas():
    return f"""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <title>Autos Colombia · Usuarios del Sistema y Roles</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>body {{ font-family: 'Inter', sans-serif; background-color: #F4F7FA; color: #1E293B; }}</style>
</head>
<body class="min-h-screen flex flex-col justify-between">
  {render_navbar('cuentas')}

  <main class="max-w-7xl w-full mx-auto px-6 py-8 flex-grow">
    <div class="mb-7">
      <p class="text-[11px] font-semibold tracking-wider text-slate-400 uppercase">SEGURIDAD Y CONTROL DE ACCESO</p>
      <h1 class="text-2xl font-bold text-slate-900 mt-0.5">Usuarios del Sistema y Permisos</h1>
      <p class="text-sm text-slate-500 mt-1">Administra las cuentas de acceso con rol ADMINISTRADOR u OPERADOR.</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
      <div class="lg:col-span-4 bg-white rounded-xl border border-slate-200/80 shadow-sm p-6">
        <h2 class="text-base font-bold text-slate-900">Crear Cuenta de Acceso</h2>
        <p class="text-xs text-slate-400 mt-0.5 mb-5">Solo el perfil ADMINISTRADOR puede crear o modificar cuentas.</p>

        <form id="formCuenta" class="space-y-4">
          <div>
            <label class="block text-xs font-medium text-slate-700 mb-1">Nombre completo</label>
            <input type="text" id="nombreCuenta" required placeholder="Ej. Laura Operadora"
              class="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg" />
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-700 mb-1">Correo de acceso</label>
            <input type="email" id="correoCuenta" required placeholder="usuario@autoscolombia.com"
              class="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg" />
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-700 mb-1">Contraseña</label>
            <input type="password" id="passCuenta" required placeholder="Mínimo 4 caracteres"
              class="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg" />
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-700 mb-1">Rol y permisos</label>
            <select id="rolCuenta" class="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg bg-white">
              <option value="OPERADOR">OPERADOR (Entrada y Salida)</option>
              <option value="ADMINISTRADOR">ADMINISTRADOR (Acceso Total)</option>
            </select>
          </div>
          <div id="alertaCuenta" class="hidden text-xs p-2.5 rounded-lg"></div>
          <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium text-sm py-2.5 rounded-lg transition cursor-pointer">
            Crear Cuenta de Usuario
          </button>
        </form>
      </div>

      <div class="lg:col-span-8 bg-white rounded-xl border border-slate-200/80 shadow-sm p-6">
        <h2 class="text-base font-bold text-slate-900 mb-4">Cuentas Registradas en PostgreSQL</h2>
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="border-b border-slate-100 text-[11px] font-semibold text-slate-400 uppercase">
              <th class="py-3 px-2">ID</th>
              <th class="py-3 px-2">Nombre</th>
              <th class="py-3 px-2">Correo</th>
              <th class="py-3 px-2">Rol</th>
              <th class="py-3 px-2">Estado</th>
              <th class="py-3 px-2 text-right">Acción</th>
            </tr>
          </thead>
          <tbody id="tablaCuentas" class="divide-y divide-slate-100 text-xs"></tbody>
        </table>
      </div>
    </div>
  </main>

  <script>
    function getRolActual() {{
      const u = JSON.parse(localStorage.getItem('autos_user') || '{{}}');
      return u.rol || 'OPERADOR';
    }}
    async function cargarCuentas() {{
      const res = await fetch('/auth/cuentas');
      const data = await res.json();
      const tbody = document.getElementById('tablaCuentas');
      tbody.innerHTML = (data.cuentas || []).map(c => `
        <tr>
          <td class="py-3 px-2 text-slate-400">#${{c.id_cuenta}}</td>
          <td class="py-3 px-2 font-semibold text-slate-800">${{c.nombre}}</td>
          <td class="py-3 px-2 text-slate-600">${{c.correo}}</td>
          <td class="py-3 px-2"><span class="px-2 py-0.5 rounded font-semibold ${{c.rol === 'ADMINISTRADOR' ? 'bg-blue-50 text-blue-600' : 'bg-slate-100 text-slate-700'}}">${{c.rol}}</span></td>
          <td class="py-3 px-2"><span class="px-2 py-0.5 rounded-full ${{c.estado === 'ACTIVO' ? 'bg-emerald-50 text-emerald-600' : 'bg-rose-50 text-rose-600'}}">${{c.estado}}</span></td>
          <td class="py-3 px-2 text-right">
            <button onclick="toggleCuenta(${{c.id_cuenta}}, '${{c.estado === 'ACTIVO' ? 'INACTIVO' : 'ACTIVO'}}')" class="px-2 py-1 rounded bg-slate-100 hover:bg-slate-200 text-[11px] cursor-pointer">
              ${{c.estado === 'ACTIVO' ? 'Desactivar' : 'Activar'}}
            </button>
          </td>
        </tr>
      `).join('');
    }}
    async function toggleCuenta(id, estado) {{
      const res = await fetch(`/auth/cuentas/${{id}}/estado?nuevo_estado=${{estado}}&rol_solicitante=${{getRolActual()}}`, {{ method: 'PATCH' }});
      const data = await res.json();
      const alerta = document.getElementById('alertaCuenta');
      alerta.className = data.exito ? 'text-xs p-2.5 rounded-lg bg-emerald-50 text-emerald-700' : 'text-xs p-2.5 rounded-lg bg-rose-50 text-rose-600';
      alerta.innerText = data.mensaje;
      alerta.classList.remove('hidden');
      cargarCuentas();
    }}
    document.getElementById('formCuenta').addEventListener('submit', async (e) => {{
      e.preventDefault();
      const params = new URLSearchParams({{
        nombre_completo: document.getElementById('nombreCuenta').value,
        correo: document.getElementById('correoCuenta').value,
        password: document.getElementById('passCuenta').value,
        rol: document.getElementById('rolCuenta').value,
        rol_solicitante: getRolActual()
      }});
      const res = await fetch(`/auth/cuentas?${{params.toString()}}`, {{ method: 'POST' }});
      const data = await res.json();
      const alerta = document.getElementById('alertaCuenta');
      alerta.className = data.exito ? 'text-xs p-2.5 rounded-lg bg-emerald-50 text-emerald-700' : 'text-xs p-2.5 rounded-lg bg-rose-50 text-rose-600';
      alerta.innerText = data.mensaje;
      alerta.classList.remove('hidden');
      if (data.exito) {{ document.getElementById('formCuenta').reset(); cargarCuentas(); }}
    }});
    cargarCuentas();
  </script>
</body>
</html>
"""

# =========================================================================
# VISTA 1: REGISTRO DE ENTRADA (/entrada-vista)
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
            <select id="selectPlaca" required class="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg bg-white"></select>
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-700 mb-1">Celda disponible asignada</label>
            <select id="selectCelda" required class="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg bg-white"></select>
          </div>
          <div id="alertaEntrada" class="hidden text-xs p-2.5 rounded-lg"></div>
          <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium text-sm py-2.5 px-4 rounded-lg shadow-sm transition cursor-pointer">
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
              <tr class="border-b border-slate-100 text-[11px] font-semibold text-slate-400 uppercase">
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

  <script>
    async function cargarDatosEntrada() {{
      const [resOcup, resActivos, resVeh] = await Promise.all([
        fetch('/ocupacion'), fetch('/ingresos-activos'), fetch('/usuarios-vehiculos')
      ]);
      const dataOcup = await resOcup.json();
      const dataActivos = await resActivos.json();
      const dataVeh = await resVeh.json();

      const vehiculos = (dataVeh.registros || []).filter(v => v.Placa);
      document.getElementById('selectPlaca').innerHTML = vehiculos.length
        ? vehiculos.map(v => `<option value="${{v.Placa}}">${{v.Placa}} · ${{v.Propietario}} (${{v.Tipo}} - ${{v.Estado}})</option>`).join('')
        : '<option value="">Sin vehículos registrados</option>';

      const disponibles = (dataOcup.celdas || []).filter(c => c.estado === 'DISPONIBLE');
      document.getElementById('selectCelda').innerHTML = disponibles.length
        ? disponibles.map(c => `<option value="${{c.id_celda}}">${{c.numero_celda}} (${{c.tipo_vehiculo}})</option>`).join('')
        : '<option value="">No hay celdas disponibles</option>';

      const registros = dataActivos.registros || [];
      document.getElementById('badgeActivos').innerText = `${{registros.length}} activos`;
      document.getElementById('tablaActivos').innerHTML = registros.length
        ? registros.map(r => `
          <tr>
            <td class="py-3 px-2 text-slate-400">#${{r.id_registro}}</td>
            <td class="py-3 px-2"><span class="px-2 py-0.5 bg-slate-100 border rounded font-semibold">${{r.placa}}</span></td>
            <td class="py-3 px-2 font-medium">${{r.propietario}}</td>
            <td class="py-3 px-2">${{r.tipo_vehiculo}}</td>
            <td class="py-3 px-2 font-semibold text-blue-600">${{r.numero_celda}}</td>
            <td class="py-3 px-2 text-slate-500">${{r.fecha_hora_ingreso}}</td>
            <td class="py-3 px-2"><span class="px-2.5 py-0.5 rounded-full text-[11px] bg-emerald-50 text-emerald-600">En parqueadero</span></td>
          </tr>`).join('')
        : '<tr><td colspan="7" class="py-6 text-center text-slate-400">No hay vehículos dentro en este momento.</td></tr>';
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
      if (data.exito) cargarDatosEntrada();
    }});
    cargarDatosEntrada();
  </script>
</body>
</html>
"""

# =========================================================================
# VISTA 2: SALIDA Y OCUPACIÓN (/salida-vista)
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
      <p class="text-sm text-slate-500 mt-1">Registra la salida de vehículos activos y libera automáticamente la celda asignada.</p>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div class="bg-white rounded-xl border p-5"><p class="text-xs text-slate-400">Total Celdas</p><p id="kpiTotal" class="text-2xl font-bold mt-1">0</p></div>
      <div class="bg-white rounded-xl border p-5"><p class="text-xs text-emerald-600">Disponibles</p><p id="kpiDisponibles" class="text-2xl font-bold text-emerald-600 mt-1">0</p></div>
      <div class="bg-white rounded-xl border p-5"><p class="text-xs text-rose-600">Ocupadas</p><p id="kpiOcupadas" class="text-2xl font-bold text-rose-600 mt-1">0</p></div>
    </div>

    <div id="alertaSalida" class="hidden text-xs p-3 rounded-lg"></div>

    <div class="bg-white rounded-xl border p-6">
      <h2 class="text-base font-bold mb-4">Vehículos Activos Pendientes de Salida</h2>
      <table class="w-full text-left border-collapse">
        <thead>
          <tr class="border-b text-[11px] font-semibold text-slate-400 uppercase">
            <th class="py-3 px-2">ID</th>
            <th class="py-3 px-2">Placa</th>
            <th class="py-3 px-2">Propietario</th>
            <th class="py-3 px-2">Celda</th>
            <th class="py-3 px-2">Ingreso</th>
            <th class="py-3 px-2 text-right">Acción</th>
          </tr>
        </thead>
        <tbody id="tablaSalidas" class="divide-y text-xs"></tbody>
      </table>
    </div>
  </main>

  <script>
    async function cargarSalidaYOcupacion() {{
      const [resOcup, resActivos] = await Promise.all([fetch('/ocupacion'), fetch('/ingresos-activos')]);
      const dataOcup = await resOcup.json();
      const dataActivos = await resActivos.json();
      document.getElementById('kpiTotal').innerText = dataOcup.total_celdas;
      document.getElementById('kpiDisponibles').innerText = dataOcup.disponibles;
      document.getElementById('kpiOcupadas').innerText = dataOcup.ocupadas;
      const registros = dataActivos.registros || [];
      document.getElementById('tablaSalidas').innerHTML = registros.length
        ? registros.map(r => `
          <tr>
            <td class="py-3 px-2">#${{r.id_registro}}</td>
            <td class="py-3 px-2 font-semibold">${{r.placa}}</td>
            <td class="py-3 px-2">${{r.propietario}}</td>
            <td class="py-3 px-2 font-bold text-rose-600">${{r.numero_celda}}</td>
            <td class="py-3 px-2">${{r.fecha_hora_ingreso}}</td>
            <td class="py-3 px-2 text-right">
              <button onclick="procesarSalida(${{r.id_registro}})" class="bg-blue-600 hover:bg-blue-700 text-white text-xs px-3 py-1.5 rounded-lg cursor-pointer">
                Registrar Salida
              </button>
            </td>
          </tr>`).join('')
        : '<tr><td colspan="6" class="py-6 text-center text-slate-400">No hay vehículos dentro.</td></tr>';
    }}
    async function procesarSalida(id) {{
      const res = await fetch(`/salida?id_registro=${{id}}`, {{ method: 'POST' }});
      const data = await res.json();
      const alerta = document.getElementById('alertaSalida');
      alerta.className = data.exito ? 'text-xs p-3 rounded-lg bg-emerald-50 text-emerald-700' : 'text-xs p-3 rounded-lg bg-rose-50 text-rose-600';
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
# VISTA 3: PROPIETARIOS Y VEHÍCULOS (/) — CON BOTÓN ELIMINAR, ACTIVAR Y BUSCAR
# =========================================================================

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def interfaz_usuarios():
    return f"""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <title>Autos Colombia · Propietarios y vehículos</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>body {{ font-family: 'Inter', sans-serif; background-color: #F4F7FA; color: #1E293B; }}</style>
</head>
<body class="min-h-screen flex flex-col justify-between">
  {render_navbar('usuarios')}

  <main class="max-w-7xl w-full mx-auto px-6 py-8 flex-grow">
    <div class="mb-7">
      <p class="text-[11px] font-semibold tracking-wider text-slate-400 uppercase">ADMINISTRACIÓN DE CLIENTES</p>
      <h1 class="text-2xl font-bold text-slate-900 mt-0.5">Propietarios y vehículos</h1>
      <p class="text-sm text-slate-500 mt-1">Registra clientes, administra mensualidades activas e inactivas y asigna celdas iniciales.</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
      <div class="lg:col-span-4 bg-white rounded-xl border border-slate-200/80 shadow-sm p-6">
        <h2 class="text-base font-bold text-slate-900">Registrar Propietario y Vehículo</h2>
        <p class="text-xs text-slate-400 mt-0.5 mb-5">Crea el usuario, vincula su vehículo y define la vigencia.</p>

        <form id="registroForm" class="space-y-3.5">
          <div>
            <label class="block text-xs font-medium text-slate-700 mb-1">Nombre completo</label>
            <input type="text" id="nombre" required placeholder="Ej. Carlos Rodríguez"
              class="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg" />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-medium text-slate-700 mb-1">Documento</label>
              <input type="text" id="documento" required placeholder="1023456789"
                class="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg" />
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-700 mb-1">Teléfono</label>
              <input type="text" id="telefono" placeholder="3001234567"
                class="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg" />
            </div>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-medium text-slate-700 mb-1">Placa</label>
              <input type="text" id="placa" required placeholder="ABC-999"
                class="w-full px-3 py-2 text-sm uppercase border border-slate-200 rounded-lg" />
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-700 mb-1">Tipo</label>
              <select id="tipo_vehiculo" class="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg bg-white">
                <option value="CARRO">Carro</option>
                <option value="MOTO">Moto</option>
              </select>
            </div>
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-700 mb-1">Estado mensualidad</label>
            <select id="estado_mensualidad" class="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg bg-white">
              <option value="ACTIVO">Activo</option>
              <option value="INACTIVO">Inactivo</option>
            </select>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-medium text-slate-700 mb-1">Inicio vigencia</label>
              <input type="date" id="fecha_inicio" required class="w-full px-2.5 py-2 text-xs border border-slate-200 rounded-lg" />
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-700 mb-1">Fin vigencia</label>
              <input type="date" id="fecha_fin" required class="w-full px-2.5 py-2 text-xs border border-slate-200 rounded-lg" />
            </div>
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-700 mb-1">Celda inicial (opcional)</label>
            <select id="celda_inicial" class="w-full px-3 py-2 text-xs border border-slate-200 rounded-lg bg-white">
              <option value="">No asignar celda ahora</option>
            </select>
          </div>
          <div id="alertaMensaje" class="hidden text-xs p-2.5 rounded-lg"></div>
          <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium text-sm py-2.5 rounded-lg transition cursor-pointer">
            Guardar Propietario y Vehículo
          </button>
        </form>
      </div>

      <div class="lg:col-span-8 bg-white rounded-xl border border-slate-200/80 shadow-sm p-6">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
          <div>
            <h2 class="text-base font-bold text-slate-900">Propietarios y Vehículos Registrados</h2>
            <p class="text-xs text-slate-400 mt-0.5">Filtra por placa, documento o nombre y gestiona su estado o eliminación.</p>
          </div>
          <div class="flex items-center space-x-2">
            <input type="text" id="inputBuscar" onkeyup="cargarUsuarios()" placeholder="Buscar placa o cédula..."
              class="px-3 py-1.5 text-xs border border-slate-200 rounded-lg" />
            <span id="contadorUsuarios" class="px-2.5 py-1 text-xs font-semibold text-blue-600 bg-blue-50 rounded-full">0</span>
          </div>
        </div>

        <div id="alertaTabla" class="hidden mb-3 text-xs p-2.5 rounded-lg"></div>

        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="border-b border-slate-100 text-[11px] font-semibold text-slate-400 uppercase">
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
      </div>
    </div>
  </main>

  <script>
    function getRolActual() {{
      return (JSON.parse(localStorage.getItem('autos_user') || '{{}}')).rol || 'OPERADOR';
    }}
    async function cargarCeldasSelect() {{
      const res = await fetch('/ocupacion');
      const data = await res.json();
      const disp = (data.celdas || []).filter(c => c.estado === 'DISPONIBLE');
      document.getElementById('celda_inicial').innerHTML = '<option value="">No asignar celda ahora</option>' +
        disp.map(c => `<option value="${{c.id_celda}}">${{c.numero_celda}} (${{c.tipo_vehiculo}})</option>`).join('');
    }}
    async function cargarUsuarios() {{
      const q = document.getElementById('inputBuscar').value;
      const url = q ? `/usuarios-vehiculos?buscar=${{encodeURIComponent(q)}}` : '/usuarios-vehiculos';
      const res = await fetch(url);
      const data = await res.json();
      const lista = data.registros || [];
      document.getElementById('contadorUsuarios').innerText = `${{lista.length}} registros`;
      document.getElementById('tablaCuerpo').innerHTML = lista.map(u => `
        <tr>
          <td class="py-3 px-2 font-semibold text-slate-800">${{u.Propietario}}</td>
          <td class="py-3 px-2 text-slate-600">${{u.Documento}}</td>
          <td class="py-3 px-2"><span class="px-2 py-0.5 bg-slate-100 border rounded font-semibold">${{u.Placa || 'N/A'}}</span></td>
          <td class="py-3 px-2">${{u.Tipo}}</td>
          <td class="py-3 px-2 text-slate-500">${{u.Vigencia}}</td>
          <td class="py-3 px-2">
            <span class="px-2 py-0.5 rounded-full font-medium ${{u.Estado === 'ACTIVO' ? 'bg-emerald-50 text-emerald-600' : 'bg-rose-50 text-rose-600'}}">
              ${{u.Estado}}
            </span>
          </td>
          <td class="py-3 px-2 text-right space-x-1 whitespace-nowrap">
            <button onclick="cambiarEstado('${{u.Placa}}', '${{u.Estado === 'ACTIVO' ? 'INACTIVO' : 'ACTIVO'}}')"
              class="px-2 py-1 rounded bg-blue-50 hover:bg-blue-100 text-blue-600 font-medium cursor-pointer">
              ${{u.Estado === 'ACTIVO' ? 'Desactivar' : 'Activar'}}
            </button>
            <button onclick="borrarUsuario(${{u.id_usuario}})"
              class="px-2 py-1 rounded bg-rose-50 hover:bg-rose-100 text-rose-600 font-medium cursor-pointer">
              Eliminar
            </button>
          </td>
        </tr>`).join('');
      cargarCeldasSelect();
    }}
    async function cambiarEstado(placa, estado) {{
      const res = await fetch(`/vehiculos/${{placa}}/estado?nuevo_estado=${{estado}}`, {{ method: 'PATCH' }});
      const data = await res.json();
      mostrarAlerta(data);
      cargarUsuarios();
    }}
    async function borrarUsuario(id) {{
      const res = await fetch(`/usuarios/${{id}}?rol_solicitante=${{getRolActual()}}`, {{ method: 'DELETE' }});
      const data = await res.json();
      mostrarAlerta(data);
      cargarUsuarios();
    }}
    function mostrarAlerta(data) {{
      const a = document.getElementById('alertaTabla');
      a.className = data.exito
        ? 'mb-3 text-xs p-2.5 rounded-lg bg-emerald-50 text-emerald-700 border border-emerald-200'
        : 'mb-3 text-xs p-2.5 rounded-lg bg-rose-50 text-rose-600 border border-rose-200';
      a.innerText = data.mensaje;
      a.classList.remove('hidden');
    }}
    document.getElementById('registroForm').addEventListener('submit', async (e) => {{
      e.preventDefault();
      const params = new URLSearchParams({{
        nombre: document.getElementById('nombre').value,
        documento: document.getElementById('documento').value,
        telefono: document.getElementById('telefono').value,
        placa: document.getElementById('placa').value,
        tipo_vehiculo: document.getElementById('tipo_vehiculo').value,
        estado_mensualidad: document.getElementById('estado_mensualidad').value,
        fecha_inicio: document.getElementById('fecha_inicio').value,
        fecha_fin: document.getElementById('fecha_fin').value
      }});
      const c = document.getElementById('celda_inicial').value;
      if (c) params.append('id_celda_inicial', c);
      const res = await fetch(`/usuarios-vehiculos?${{params.toString()}}`, {{ method: 'POST' }});
      const data = await res.json();
      const a = document.getElementById('alertaMensaje');
      a.className = data.exito ? 'text-xs p-2.5 rounded-lg bg-emerald-50 text-emerald-700' : 'text-xs p-2.5 rounded-lg bg-rose-50 text-rose-600';
      a.innerText = data.mensaje;
      a.classList.remove('hidden');
      if (data.exito) {{ document.getElementById('registroForm').reset(); cargarUsuarios(); }}
    }});
    cargarUsuarios();
  </script>
</body>
</html>
"""

# =========================================================================
# VISTA 4: CELDAS (/celdas-vista) — CON BOTÓN CREAR Y ELIMINAR CELDA
# =========================================================================

@app.get("/celdas-vista", response_class=HTMLResponse, include_in_schema=False)
def interfaz_celdas():
    return f"""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <title>Autos Colombia · Celdas</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>body {{ font-family: 'Inter', sans-serif; background-color: #F4F7FA; color: #1E293B; }}</style>
</head>
<body class="min-h-screen flex flex-col justify-between">
  {render_navbar('celdas')}

  <main class="max-w-7xl w-full mx-auto px-8 py-8 flex-grow space-y-6">
    <div>
      <p class="text-[11px] font-semibold tracking-wider text-slate-400 uppercase">ADMINISTRACIÓN DE ESPACIOS</p>
      <h1 class="text-2xl font-bold text-slate-900 mt-0.5">Celdas de parqueo</h1>
    </div>

    <div class="bg-white rounded-xl border p-6">
      <form id="formCelda" class="grid grid-cols-1 md:grid-cols-12 gap-4 items-end">
        <div class="md:col-span-5">
          <label class="block text-xs font-medium mb-1">Código de celda</label>
          <input type="text" id="numero_celda" required placeholder="ej. M-203 o C-103" class="w-full px-3.5 py-2.5 text-sm uppercase border rounded-lg" />
        </div>
        <div class="md:col-span-5">
          <label class="block text-xs font-medium mb-1">Tipo</label>
          <select id="tipo_celda" class="w-full px-3.5 py-2.5 text-sm border rounded-lg bg-white">
            <option value="CARRO">Carro</option>
            <option value="MOTO">Moto</option>
          </select>
        </div>
        <div class="md:col-span-2">
          <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium text-sm py-2.5 rounded-lg cursor-pointer">+ Crear Celda</button>
        </div>
      </form>
      <div id="alertaCelda" class="hidden mt-3 text-xs p-2.5 rounded-lg"></div>
    </div>

    <div class="bg-white rounded-xl border p-6">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div>
          <h3 class="text-xs font-bold uppercase text-slate-400 mb-3">Zona Carros</h3>
          <div id="gridCarros" class="grid grid-cols-2 gap-4"></div>
        </div>
        <div>
          <h3 class="text-xs font-bold uppercase text-slate-400 mb-3">Zona Motos</h3>
          <div id="gridMotos" class="grid grid-cols-2 gap-4"></div>
        </div>
      </div>
    </div>
  </main>

  <script>
    function getRolActual() {{ return (JSON.parse(localStorage.getItem('autos_user') || '{{}}')).rol || 'OPERADOR'; }}
    function crearTarjeta(c) {{
      const disp = c.estado === 'DISPONIBLE';
      return `<div class="rounded-xl border ${{disp ? 'border-emerald-500' : 'border-rose-500'}} p-4">
        <div class="text-xl font-bold mb-2">${{c.numero_celda}}</div>
        <div class="flex justify-between items-center">
          <span class="text-xs font-semibold ${{disp ? 'text-emerald-600' : 'text-rose-600'}}">${{c.estado}}</span>
          ${{disp ? `<button onclick="borrarCelda(${{c.id_celda}})" class="text-xs text-rose-600 hover:underline cursor-pointer">Eliminar</button>` : ''}}
        </div>
      </div>`;
    }}
    async function borrarCelda(id) {{
      const res = await fetch(`/celdas/${{id}}?rol_solicitante=${{getRolActual()}}`, {{ method: 'DELETE' }});
      const data = await res.json();
      const a = document.getElementById('alertaCelda');
      a.className = data.exito ? 'mt-3 text-xs p-2.5 rounded-lg bg-emerald-50 text-emerald-700' : 'mt-3 text-xs p-2.5 rounded-lg bg-rose-50 text-rose-600';
      a.innerText = data.mensaje;
      a.classList.remove('hidden');
      cargarCeldas();
    }}
    async function cargarCeldas() {{
      const res = await fetch('/ocupacion');
      const data = await res.json();
      const celdas = data.celdas || [];
      document.getElementById('gridCarros').innerHTML = celdas.filter(c => c.tipo_vehiculo === 'CARRO').map(crearTarjeta).join('');
      document.getElementById('gridMotos').innerHTML = celdas.filter(c => c.tipo_vehiculo === 'MOTO').map(crearTarjeta).join('');
    }}
    document.getElementById('formCelda').addEventListener('submit', async (e) => {{
      e.preventDefault();
      const params = new URLSearchParams({{
        numero_celda: document.getElementById('numero_celda').value,
        tipo_vehiculo: document.getElementById('tipo_celda').value,
        rol_solicitante: getRolActual()
      }});
      const res = await fetch(`/celdas?${{params.toString()}}`, {{ method: 'POST' }});
      const data = await res.json();
      const a = document.getElementById('alertaCelda');
      a.className = data.exito ? 'mt-3 text-xs p-2.5 rounded-lg bg-emerald-50 text-emerald-700' : 'mt-3 text-xs p-2.5 rounded-lg bg-rose-50 text-rose-600';
      a.innerText = data.mensaje;
      a.classList.remove('hidden');
      if (data.exito) {{ document.getElementById('formCelda').reset(); cargarCeldas(); }}
    }});
    cargarCeldas();
  </script>
</body>
</html>
"""

# =========================================================================
# VISTA 5: GESTIÓN DE PAGOS Y RECIBOS (/pagos-vista)
# =========================================================================

@app.get("/pagos-vista", response_class=HTMLResponse, include_in_schema=False)
def interfaz_pagos():
    return f"""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <title>Autos Colombia · Gestión de Pagos</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>body {{ font-family: 'Inter', sans-serif; background-color: #F4F7FA; color: #1E293B; }}</style>
</head>
<body class="min-h-screen flex flex-col justify-between">
  {render_navbar('pagos')}

  <main class="max-w-7xl w-full mx-auto px-6 py-8 flex-grow space-y-6">
    <div>
      <p class="text-[11px] font-semibold tracking-wider text-slate-400 uppercase">GESTIÓN FINANCIERA</p>
      <h1 class="text-2xl font-bold text-slate-900 mt-0.5">Pagos y Mensualidades</h1>
      <p class="text-sm text-slate-500 mt-1">Registra pagos de mensualidad, genera comprobantes y activa automáticamente la vigencia.</p>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div class="bg-white rounded-xl border p-5"><p class="text-xs text-slate-400">Total Recaudado</p><p id="kpiRecaudado" class="text-2xl font-bold text-blue-600 mt-1">$0</p></div>
      <div class="bg-white rounded-xl border p-5"><p class="text-xs text-emerald-600">Pagos Registrados</p><p id="kpiTransacciones" class="text-2xl font-bold text-emerald-600 mt-1">0</p></div>
      <div class="bg-white rounded-xl border p-5"><p class="text-xs text-slate-400">Tarifas Estándar</p><p class="text-sm font-semibold mt-2">Carro: $120.000 · Moto: $70.000</p></div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
      <div class="lg:col-span-4 bg-white rounded-xl border p-6">
        <h2 class="text-base font-bold mb-4">Registrar Pago de Mensualidad</h2>
        <form id="formPago" class="space-y-4">
          <div>
            <label class="block text-xs font-medium mb-1">Vehículo</label>
            <select id="selectVehiculoPago" onchange="actualizarTarifa()" required class="w-full px-3 py-2 text-sm border rounded-lg bg-white"></select>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-medium mb-1">Valor ($ COP)</label>
              <input type="number" id="montoPago" required value="120000" class="w-full px-3 py-2 text-sm border rounded-lg" />
            </div>
            <div>
              <label class="block text-xs font-medium mb-1">Método</label>
              <select id="metodoPago" class="w-full px-3 py-2 text-sm border rounded-lg bg-white">
                <option value="Efectivo">Efectivo</option>
                <option value="Transferencia">Transferencia</option>
                <option value="Tarjeta">Tarjeta</option>
              </select>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div><label class="block text-xs font-medium mb-1">Inicio vigencia</label><input type="date" id="periodoInicio" required class="w-full px-2.5 py-2 text-xs border rounded-lg" /></div>
            <div><label class="block text-xs font-medium mb-1">Fin vigencia</label><input type="date" id="periodoFin" required class="w-full px-2.5 py-2 text-xs border rounded-lg" /></div>
          </div>
          <div id="alertaPago" class="hidden text-xs p-2.5 rounded-lg"></div>
          <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium text-sm py-2.5 rounded-lg cursor-pointer">
            Registrar Pago y Activar
          </button>
        </form>
      </div>

      <div class="lg:col-span-8 bg-white rounded-xl border p-6">
        <h2 class="text-base font-bold mb-4">Historial de Pagos y Comprobantes</h2>
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="border-b text-[11px] font-semibold text-slate-400 uppercase">
              <th class="py-3 px-2">Recibo</th>
              <th class="py-3 px-2">Propietario</th>
              <th class="py-3 px-2">Placa</th>
              <th class="py-3 px-2">Método</th>
              <th class="py-3 px-2">Vigencia</th>
              <th class="py-3 px-2">Monto</th>
              <th class="py-3 px-2">Estado</th>
              <th class="py-3 px-2 text-right">Acciones</th>
            </tr>
          </thead>
          <tbody id="tablaPagos" class="divide-y text-xs"></tbody>
        </table>
      </div>
    </div>

    <div id="modalComprobante" class="hidden fixed inset-0 bg-slate-900/40 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl max-w-md w-full p-6 shadow-xl">
        <div class="flex justify-between border-b pb-3 mb-4">
          <h3 class="text-lg font-bold">Comprobante de Pago</h3>
          <span id="reciboCodigo" class="px-2.5 py-1 bg-slate-100 rounded-lg text-xs font-bold">REC-0001</span>
        </div>
        <div id="reciboDetalle" class="space-y-2 text-xs"></div>
        <div class="mt-6 flex justify-end space-x-2">
          <button onclick="window.print()" class="px-4 py-2 rounded-lg border text-xs cursor-pointer">Imprimir</button>
          <button onclick="document.getElementById('modalComprobante').classList.add('hidden')" class="px-4 py-2 rounded-lg bg-blue-600 text-white text-xs cursor-pointer">Cerrar</button>
        </div>
      </div>
    </div>
  </main>

  <script>
    let mapaVeh = {{}};
    function getRolActual() {{ return (JSON.parse(localStorage.getItem('autos_user') || '{{}}')).rol || 'OPERADOR'; }}
    function initFechas() {{
      const hoy = new Date(); const fin = new Date(); fin.setDate(hoy.getDate() + 30);
      document.getElementById('periodoInicio').value = hoy.toISOString().split('T')[0];
      document.getElementById('periodoFin').value = fin.toISOString().split('T')[0];
    }}
    function actualizarTarifa() {{
      const p = document.getElementById('selectVehiculoPago').value;
      document.getElementById('montoPago').value = mapaVeh[p] === 'MOTO' ? 70000 : 120000;
    }}
    async function cargarPagos() {{
      const [rV, rP] = await Promise.all([fetch('/usuarios-vehiculos'), fetch('/pagos')]);
      const dV = await rV.json(); const dP = await rP.json();
      const vehs = (dV.registros || []).filter(v => v.Placa);
      mapaVeh = {{}}; vehs.forEach(v => mapaVeh[v.Placa] = v.Tipo);
      document.getElementById('selectVehiculoPago').innerHTML = vehs.map(v => `<option value="${{v.Placa}}">${{v.Placa}} · ${{v.Propietario}} (${{v.Tipo}} - ${{v.Estado}})</option>`).join('');
      actualizarTarifa();
      document.getElementById('kpiRecaudado').innerText = `$${{(dP.total_recaudado || 0).toLocaleString('es-CO')}}`;
      document.getElementById('kpiTransacciones').innerText = dP.total_transacciones || 0;
      document.getElementById('tablaPagos').innerHTML = (dP.registros || []).map(p => `
        <tr>
          <td class="py-3 px-2 font-bold text-blue-600">${{p.numero_recibo}}</td>
          <td class="py-3 px-2">${{p.propietario}}</td>
          <td class="py-3 px-2 font-semibold">${{p.placa}}</td>
          <td class="py-3 px-2">${{p.metodo_pago}}</td>
          <td class="py-3 px-2">${{p.vigencia}}</td>
          <td class="py-3 px-2 font-semibold">$${{p.monto.toLocaleString('es-CO')}}</td>
          <td class="py-3 px-2"><span class="px-2 py-0.5 rounded-full ${{p.estado_pago === 'PAGADO' ? 'bg-emerald-50 text-emerald-600' : 'bg-rose-50 text-rose-600'}}">${{p.estado_pago}}</span></td>
          <td class="py-3 px-2 text-right space-x-1">
            <button onclick='verRecibo(${{JSON.stringify(p)}})' class="px-2 py-1 rounded bg-blue-50 text-blue-600 cursor-pointer">Recibo</button>
            ${{p.estado_pago === 'PAGADO' ? `<button onclick="anularPago(${{p.id_pago}})" class="px-2 py-1 rounded bg-rose-50 text-rose-600 cursor-pointer">Anular</button>` : ''}}
          </td>
        </tr>`).join('');
    }}
    function verRecibo(p) {{
      document.getElementById('reciboCodigo').innerText = p.numero_recibo;
      document.getElementById('reciboDetalle').innerHTML = `<p><strong>Propietario:</strong> ${{p.propietario}} (${{p.documento}})</p><p><strong>Placa:</strong> ${{p.placa}} (${{p.tipo_vehiculo}})</p><p><strong>Vigencia:</strong> ${{p.vigencia}}</p><p><strong>Método:</strong> ${{p.metodo_pago}}</p><p class="text-sm text-blue-600 font-bold pt-2 border-t">Total Pagado: $${{p.monto.toLocaleString('es-CO')}} COP</p>`;
      document.getElementById('modalComprobante').classList.remove('hidden');
    }}
    async function anularPago(id) {{
      const res = await fetch(`/pagos/${{id}}/anular?rol_solicitante=${{getRolActual()}}`, {{ method: 'PATCH' }});
      const data = await res.json();
      const a = document.getElementById('alertaPago');
      a.className = data.exito ? 'text-xs p-2.5 rounded-lg bg-emerald-50 text-emerald-700' : 'text-xs p-2.5 rounded-lg bg-rose-50 text-rose-600';
      a.innerText = data.mensaje;
      a.classList.remove('hidden');
      cargarPagos();
    }}
    document.getElementById('formPago').addEventListener('submit', async (e) => {{
      e.preventDefault();
      const params = new URLSearchParams({{
        placa: document.getElementById('selectVehiculoPago').value,
        monto: document.getElementById('montoPago').value,
        metodo_pago: document.getElementById('metodoPago').value,
        periodo_inicio: document.getElementById('periodoInicio').value,
        periodo_fin: document.getElementById('periodoFin').value
      }});
      const res = await fetch(`/pagos?${{params.toString()}}`, {{ method: 'POST' }});
      const data = await res.json();
      const a = document.getElementById('alertaPago');
      a.className = data.exito ? 'text-xs p-2.5 rounded-lg bg-emerald-50 text-emerald-700' : 'text-xs p-2.5 rounded-lg bg-rose-50 text-rose-600';
      a.innerText = data.mensaje;
      a.classList.remove('hidden');
      if (data.exito) cargarPagos();
    }});
    initFechas(); cargarPagos();
  </script>
</body>
</html>
"""

# =========================================================================
# ENDPOINTS API REST COMPLETOS (SWAGGER /docs)
# =========================================================================

@app.post("/auth/login", tags=["Autenticación y Roles"])
def login(correo: str = Query(...), password: str = Query(...)):
    return servicio.autenticar_usuario(correo, password)

@app.post("/auth/cuentas", tags=["Autenticación y Roles"])
def crear_cuenta(nombre_completo: str = Query(...), correo: str = Query(...), password: str = Query(...), rol: Literal["ADMINISTRADOR", "OPERADOR"] = Query("OPERADOR"), rol_solicitante: str = Query("ADMINISTRADOR")):
    return servicio.crear_cuenta_sistema(nombre_completo, correo, password, rol, rol_solicitante)

@app.get("/auth/cuentas", tags=["Autenticación y Roles"])
def listar_cuentas():
    return servicio.listar_cuentas_sistema()

@app.patch("/auth/cuentas/{id_cuenta}/estado", tags=["Autenticación y Roles"])
def cambiar_estado_cuenta(id_cuenta: int, nuevo_estado: Literal["ACTIVO", "INACTIVO"] = Query(...), rol_solicitante: str = Query("ADMINISTRADOR")):
    return servicio.cambiar_estado_cuenta(id_cuenta, nuevo_estado, rol_solicitante)

@app.post("/usuarios-vehiculos", tags=["Propietarios y vehículos"])
def registrar_usuario_y_vehiculo(nombre: str = Query(...), documento: str = Query(...), telefono: str = Query(...), placa: str = Query(...), tipo_vehiculo: Literal["CARRO", "MOTO"] = Query("CARRO"), estado_mensualidad: Literal["ACTIVO", "INACTIVO"] = Query("ACTIVO"), fecha_inicio: date = Query(...), fecha_fin: date = Query(...), id_celda_inicial: Optional[int] = Query(None)):
    return servicio.registrar_usuario_y_vehiculo(nombre, documento, telefono, placa, tipo_vehiculo, estado_mensualidad, fecha_inicio, fecha_fin, id_celda_inicial)

@app.get("/usuarios-vehiculos", tags=["Propietarios y vehículos"])
def consultar_usuarios_y_vehiculos(buscar: Optional[str] = Query(None)):
    return servicio.listar_usuarios_y_vehiculos(buscar)

@app.patch("/vehiculos/{placa}/estado", tags=["Propietarios y vehículos"])
def actualizar_estado_mensualidad(placa: str, nuevo_estado: Literal["ACTIVO", "INACTIVO"] = Query(...), fecha_inicio: Optional[date] = Query(None), fecha_fin: Optional[date] = Query(None)):
    return servicio.cambiar_estado_mensualidad(placa, nuevo_estado, fecha_inicio, fecha_fin)

@app.delete("/usuarios/{id_usuario}", tags=["Propietarios y vehículos"])
def eliminar_usuario(id_usuario: int, rol_solicitante: str = Query("ADMINISTRADOR")):
    return servicio.eliminar_usuario(id_usuario, rol_solicitante)

@app.post("/celdas", tags=["Celdas"])
def crear_celda(numero_celda: str = Query(...), tipo_vehiculo: Literal["CARRO", "MOTO"] = Query("CARRO"), rol_solicitante: str = Query("ADMINISTRADOR")):
    return servicio.crear_celda(numero_celda, tipo_vehiculo, rol_solicitante)

@app.delete("/celdas/{id_celda}", tags=["Celdas"])
def eliminar_celda(id_celda: int, rol_solicitante: str = Query("ADMINISTRADOR")):
    return servicio.eliminar_celda(id_celda, rol_solicitante)

@app.get("/ocupacion", tags=["Celdas"])
def consultar_ocupacion():
    return servicio.consultar_ocupacion()

@app.get("/ingresos-activos", tags=["Registro de entrada y salida"])
def consultar_ingresos_activos():
    return servicio.listar_ingresos_activos()

@app.post("/ingreso", tags=["Registro de entrada y salida"])
def registrar_ingreso(placa: str = Query(...), id_celda: int = Query(...)):
    return servicio.registrar_ingreso(placa, id_celda)

@app.post("/salida", tags=["Registro de entrada y salida"])
def registrar_salida(id_registro: int = Query(...)):
    return servicio.registrar_salida(id_registro)

@app.post("/pagos", tags=["Gestión de pagos"])
def registrar_pago(placa: str = Query(...), monto: float = Query(...), metodo_pago: Literal["Efectivo", "Transferencia", "Tarjeta"] = Query("Efectivo"), periodo_inicio: date = Query(...), periodo_fin: date = Query(...)):
    return servicio.registrar_pago(placa, monto, metodo_pago, periodo_inicio, periodo_fin)

@app.get("/pagos", tags=["Gestión de pagos"])
def consultar_pagos(buscar: Optional[str] = Query(None)):
    return servicio.listar_pagos(buscar)

@app.patch("/pagos/{id_pago}/anular", tags=["Gestión de pagos"])
def anular_pago(id_pago: int, rol_solicitante: str = Query("ADMINISTRADOR")):
    return servicio.anular_pago(id_pago, rol_solicitante)