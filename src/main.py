import flet as ft
import urllib.parse
import json
import os
from datetime import datetime

# ====== SISTEMA DE GUARDADO ======
CONFIG_FILE = "config.json"
DATOS_FILE = "datos.json"

def cargar_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "negocio": {"nombre": "Mi Negocio", "tipo": "Bodega", "telefono": "", "direccion": ""},
        "pin": None,
        "moneda": "Bs.",
    }

def guardar_config(config):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error guardando config: {e}")

def cargar_datos():
    if os.path.exists(DATOS_FILE):
        try:
            with open(DATOS_FILE, "r", encoding="utf-8") as f:
                datos = json.load(f)
                return datos.get("fiados", []), datos.get("ventas", []), datos.get("productos", [])
        except Exception:
            pass
    return [], [], []

def guardar_datos(fiados, ventas, productos):
    try:
        with open(DATOS_FILE, "w", encoding="utf-8") as f:
            json.dump({"fiados": fiados, "ventas": ventas, "productos": productos}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error guardando datos: {e}")


def main(page: ft.Page):
    page.title = "Fiado"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.bgcolor = ft.Colors.BLUE_50 # Fondo azul muy claro
    page.window_width = 400
    page.window_height = 800

    config = cargar_config()
    datos_negocio = config["negocio"]
    moneda_actual = config.get("moneda", "Bs.")
    fiados, ventas, productos = cargar_datos()

    # ====== HELPERS ======
    def ancho_dialogo():
        return min((page.width if page.width else 400) - 40, 450)

    def formatear_monto(valor):
        numero = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{moneda_actual} {numero}"

    def abrir_whatsapp(numero, mensaje):
        numero_limpio = "".join(c for c in numero if c.isdigit())
        if numero_limpio.startswith("0"):
            numero_limpio = "58" + numero_limpio[1:]
        url = f"https://wa.me/{numero_limpio}?text={urllib.parse.quote(mensaje)}"
        page.launch_url(url)

    def refrescar_totales():
        total = sum(f["monto"] for f in fiados)
        try:
            texto_total.value = formatear_monto(total)
            texto_subtitulo_total.value = f"{len(fiados)} fiado(s) pendiente(s)" if fiados else "Tu cartera está al día ✨"
            page.update()
        except Exception:
            pass

    def mostrar_mensaje_copiable(titulo, mensaje):
        async def copiar(e):
            try: await ft.Clipboard().set(mensaje)
            except Exception: pass
            page.pop_dialog()
            page.show_dialog(ft.AlertDialog(content=ft.Text("✅ Mensaje copiado"), actions=[ft.Button("OK", on_click=lambda e: page.pop_dialog())]))
        
        page.show_dialog(ft.AlertDialog(
            title=ft.Text(titulo), content=ft.Text(mensaje, selectable=True),
            actions=[ft.Button("📋 Copiar", on_click=copiar, bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE), ft.Button("Cerrar", on_click=lambda e: page.pop_dialog())],
        ))

    def campo_texto(label, **kwargs):
        return ft.TextField(
            label=label, 
            border=ft.OutlineInputBorder(side=ft.BorderSide(1, ft.Colors.BLUE_300), border_radius=10),
            content_padding=ft.Padding.only(left=15, right=15, top=15, bottom=15),
            text_size=14, **kwargs
        )

    def boton(texto, on_click, color=ft.Colors.BLUE_700, **kwargs):
        return ft.Button(
            texto, on_click=on_click, bgcolor=color, color=ft.Colors.WHITE,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)), height=45, **kwargs
        )

    # =========================================================
    # BARRA DE NAVEGACIÓN
    # =========================================================
    def crear_bottom_appbar(index_activo):
        def item_nav(icono, titulo, index_destino):
            activo = (index_activo == index_destino)
            color = ft.Colors.BLUE_700 if activo else ft.Colors.GREY_500
            return ft.Container(
                content=ft.Column(controls=[
                    ft.Icon(icono, size=24, color=color),
                    ft.Text(titulo, size=10, color=color, weight=ft.FontWeight.BOLD if activo else ft.FontWeight.NORMAL),
                ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                on_click=lambda e: cambiar_pantalla(index_destino),
                expand=True, padding=ft.Padding.only(top=10, bottom=5)
            )

        boton_central = ft.Container(
            content=ft.Container(
                content=ft.Icon(ft.Icons.ADD, size=32, color=ft.Colors.WHITE),
                bgcolor=ft.Colors.BLUE_700, width=60, height=60, border_radius=50, alignment=ft.Alignment.CENTER,
                shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.with_opacity(0.4, ft.Colors.BLUE_700))
            ),
            on_click=lambda e: abrir_registrar_fiado(None),
            margin=ft.Margin.only(bottom=15)
        )

        return ft.BottomAppBar(
            content=ft.Row(
                controls=[
                    item_nav(ft.Icons.HOME, "Inicio", 0),
                    item_nav(ft.Icons.PEOPLE, "Fiados", 1),
                    boton_central,
                    item_nav(ft.Icons.BAR_CHART, "Ventas", 3),
                    item_nav(ft.Icons.MENU, "Menú", 4),
                ], alignment=ft.MainAxisAlignment.SPACE_AROUND,
            ),
            bgcolor=ft.Colors.WHITE, height=75, shape=ft.RoundedRectangleBorder(radius=0), padding=ft.Padding.all(0),
        )

    def cambiar_pantalla(index):
        if index == 0: mostrar_app_principal()
        elif index == 1: abrir_cartera(None)
        elif index == 3: abrir_ventas(None)
        elif index == 4: abrir_menu(None)

    # =========================================================
    # PANTALLA PRINCIPAL
    # =========================================================
    texto_total = None
    texto_subtitulo_total = None

    def mostrar_app_principal():
        nonlocal texto_total, texto_subtitulo_total
        page.controls.clear()
        page.bottom_appbar = None

        encabezado = ft.Container(
            content=ft.Column(controls=[
                ft.Text(f"Hola, {datos_negocio['nombre']} 👋", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                ft.Text(f"{datos_negocio['nombre']} - {datos_negocio['tipo']}", size=13, color=ft.Colors.GREY_600),
            ], spacing=2), padding=ft.Padding.only(left=20, right=20, top=20, bottom=10)
        )

        texto_total = ft.Text(formatear_monto(sum(f["monto"] for f in fiados)), color=ft.Colors.WHITE, size=32, weight=ft.FontWeight.BOLD)
        texto_subtitulo_total = ft.Text(f"{len(fiados)} fiado(s) pendiente(s)" if fiados else "Tu cartera está al día", color=ft.Colors.WHITE_70, size=14)

        main_card = ft.Container(
            content=ft.Column(controls=[
                ft.Text("Total por cobrar", color=ft.Colors.WHITE, size=16, weight=ft.FontWeight.BOLD),
                texto_total, texto_subtitulo_total,
                ft.Row(controls=[ft.Text("Ver lista", color=ft.Colors.WHITE, size=13), ft.Icon(ft.Icons.ARROW_FORWARD, color=ft.Colors.WHITE, size=16)], alignment=ft.MainAxisAlignment.END),
            ], spacing=5),
            gradient=ft.LinearGradient(colors=["#1E88E5", "#0D47A1"]), # Degradado azul
            padding=25, border_radius=20,
            margin=ft.Margin.only(left=20, right=20, top=10), on_click=abrir_cartera, ink=True,
        )

        page.add(ft.Column(controls=[encabezado, main_card], scroll=ft.ScrollMode.AUTO, expand=True))
        page.bottom_appbar = crear_bottom_appbar(0)
        page.update()

    # =========================================================
    # VER CARTERA
    # =========================================================
    def abrir_cartera(e):
        page.controls.clear()
        page.bottom_appbar = None
        total = sum(f["monto"] for f in fiados)

        def lista_fiados():
            if not fiados:
                return ft.Column(controls=[ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN_400, size=60), ft.Text("No hay fiados pendientes", size=16, weight=ft.FontWeight.BOLD)], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)
            
            filas = []
            for f in fiados:
                def crear_recordatorio(fiado=f):
                    def recordar(e):
                        msg = f"Hola {fiado['cliente']}, le saluda {datos_negocio['nombre']}. Le recordamos su saldo pendiente de {formatear_monto(fiado['monto'])}."
                        if fiado.get('telefono'):
                            try: abrir_whatsapp(fiado['telefono'], msg)
                            except Exception: mostrar_mensaje_copiable("Mensaje", msg)
                        else: mostrar_mensaje_copiable("Mensaje", msg)
                    return recordar

                filas.append(ft.Container(
                    content=ft.Column(controls=[
                        ft.Row(controls=[
                            ft.Container(content=ft.Icon(ft.Icons.PERSON, color=ft.Colors.WHITE, size=18), bgcolor=ft.Colors.BLUE_400, padding=8, border_radius=50),
                            ft.Column(controls=[
                                ft.Text(f["cliente"], weight=ft.FontWeight.BOLD, size=15),
                                ft.Text(f["descripcion"] or "Sin descripción", size=12, color=ft.Colors.GREY_600),
                            ], spacing=2, expand=True),
                            ft.Text(formatear_monto(f["monto"]), weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700, size=15),
                        ]),
                        ft.Text(f"📅 {f['fecha_pago'] or 'Sin fecha'} | 📞 {f['telefono'] or 'Sin teléfono'}", size=12, color=ft.Colors.GREY_500),
                        ft.Row(controls=[
                            boton("💬 Recordar", on_click=crear_recordatorio(f), color=ft.Colors.GREEN_600, expand=True),
                            boton("💵 Abonar", lambda e, fiado=f: abrir_abono(fiado), color=ft.Colors.BLUE_600, expand=True),
                        ], spacing=8),
                        ft.Row(controls=[
                            boton("📅 Editar Fecha", lambda e, fiado=f: editar_fecha(fiado), color=ft.Colors.LIGHT_BLUE_600, expand=True),
                            boton("🗑️ Eliminar", lambda e, fiado=f: eliminar_fiado(fiado), color=ft.Colors.RED_600, expand=True),
                        ], spacing=8)
                    ], spacing=10),
                    bgcolor=ft.Colors.WHITE, padding=15, border_radius=15, margin=ft.Margin.only(bottom=10),
                ))
            return ft.Column(controls=filas)

        encabezado = ft.Container(
            content=ft.Row(controls=[
                ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: mostrar_app_principal()),
                ft.Text("Fiados por cobrar", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900, expand=True),
            ]), padding=ft.Padding.only(left=10, right=10, top=20, bottom=10)
        )

        page.add(ft.Column(controls=[encabezado, ft.Container(content=lista_fiados(), padding=20)], scroll=ft.ScrollMode.AUTO, expand=True))
        page.bottom_appbar = crear_bottom_appbar(1)
        page.update()

    def abrir_abono(fiado):
        campo_abono = campo_texto(f"Monto ({moneda_actual})", keyboard_type=ft.KeyboardType.NUMBER)
        def guardar(e):
            try:
                abono = float(campo_abono.value.replace(",", "."))
                if abono > fiado["monto"]: campo_abono.error_text = "Excede"; page.update(); return
                fiado["monto"] -= abono
                if fiado["monto"] <= 0.01: fiados.remove(fiado)
                guardar_datos(fiados, ventas, productos)
                page.pop_dialog(); refrescar_totales(); abrir_cartera(None)
            except ValueError: campo_abono.error_text = "Inválido"; page.update()

        page.show_dialog(ft.AlertDialog(
            title=ft.Text("Abonar"), content=ft.Column([ft.Text(f"Cliente: {fiado['cliente']}"), campo_abono]),
            actions=[boton("Cancelar", lambda e: page.pop_dialog(), color=ft.Colors.GREY_400), boton("Guardar", guardar, color=ft.Colors.GREEN_600)]
        ))

    def editar_fecha(fiado):
        campo_fecha = campo_texto("Nueva fecha de pago", value=fiado["fecha_pago"])
        def guardar(e):
            fiado["fecha_pago"] = campo_fecha.value.strip()
            guardar_datos(fiados, ventas, productos)
            page.pop_dialog(); abrir_cartera(None)
        page.show_dialog(ft.AlertDialog(
            title=ft.Text("Editar Fecha"), content=campo_fecha,
            actions=[boton("Cancelar", lambda e: page.pop_dialog(), color=ft.Colors.GREY_400), boton("Guardar", guardar)]
        ))

    def eliminar_fiado(fiado):
        def confirmar(e):
            fiados.remove(fiado); guardar_datos(fiados, ventas, productos)
            page.pop_dialog(); refrescar_totales(); abrir_cartera(None)
        page.show_dialog(ft.AlertDialog(
            title=ft.Text("Eliminar"), content=ft.Text(f"¿Eliminar fiado de {fiado['cliente']}?"),
            actions=[boton("Cancelar", lambda e: page.pop_dialog(), color=ft.Colors.GREY_400), boton("Eliminar", confirmar, color=ft.Colors.RED_600)]
        ))

    # =========================================================
    # REGISTRAR FIADO
    # =========================================================
    def abrir_registrar_fiado(e):
        campo_cliente = campo_texto("Nombre del cliente")
        campo_telefono = campo_texto("Teléfono del cliente")
        campo_monto = campo_texto(f"Monto manual ({moneda_actual})", hint_text="Opcional si eliges productos")
        campo_fecha = campo_texto("Fecha de pago")
        
        productos_seleccionados = []
        texto_productos = ft.Text("No has seleccionado productos", size=12, color=ft.Colors.GREY_600)

        def actualizar_vista_productos():
            if not productos_seleccionados:
                texto_productos.value = "No has seleccionado productos"
            else:
                resumen = ", ".join([f"{p['cant']}x {p['nombre']}" for p in productos_seleccionados])
                texto_productos.value = f"Seleccionados: {resumen}"
                total = sum(item["precio"] * item["cant"] for item in productos_seleccionados)
                campo_monto.value = str(total)
            page.update()

        def abrir_selector_productos(e):
            if not productos:
                page.show_dialog(ft.AlertDialog(title=ft.Text("Inventario vacío"), content=ft.Text("Agrega productos al inventario primero.")))
                return

            def seleccionar(index):
                p = productos[index]
                if p["stock"] <= 0: return
                
                existente = next((item for item in productos_seleccionados if item["nombre"] == p["nombre"]), None)
                if existente:
                    existente["cant"] += 1
                else:
                    productos_seleccionados.append({"nombre": p["nombre"], "precio": p["precio"], "cant": 1, "index": index})
                
                p["stock"] -= 1
                actualizar_vista_productos()
                page.pop_dialog()
                
            filas = [ft.Container(content=ft.Row([ft.Text(p["nombre"], expand=True), ft.Text(f"Stock: {p['stock']}"), ft.IconButton(ft.Icons.ADD, on_click=lambda e, i=i: seleccionar(i))])) for i, p in enumerate(productos) if p["stock"] > 0]
            
            page.show_dialog(ft.AlertDialog(
                title=ft.Text("Seleccionar Producto"),
                content=ft.Column(filas, height=300, scroll=ft.ScrollMode.AUTO) if filas else ft.Text("No hay stock disponible"),
                actions=[boton("Cerrar", lambda e: page.pop_dialog(), color=ft.Colors.GREY_400)]
            ))

        def guardar_fiado(e):
            nombre = campo_cliente.value.strip()
            monto = campo_monto.value.strip()
            
            if not nombre or not monto:
                campo_cliente.error_text = "Falta nombre"
                campo_monto.error_text = "Falta monto o selecciona productos"
                page.update(); return
                
            monto_float = float(monto.replace(",", "."))
            
            fiados.append({
                "cliente": nombre, "telefono": campo_telefono.value.strip(),
                "monto": monto_float, "monto_original": monto_float, "abonado": 0.0,
                "fecha_pago": campo_fecha.value.strip(), "descripcion": "Productos varios" if productos_seleccionados else "Sin descripción"
            })
            
            guardar_datos(fiados, ventas, productos)
            refrescar_totales()
            page.pop_dialog()

        contenido = ft.Container(
            content=ft.Column(controls=[
                ft.Text("Nuevo Fiado", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900), ft.Divider(), 
                campo_cliente, campo_telefono, campo_fecha, 
                ft.Row(controls=[
                    ft.Column(controls=[ft.Text("Productos:", weight=ft.FontWeight.BOLD), texto_productos], expand=True),
                    ft.Button("Añadir", on_click=abrir_selector_productos, bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE)
                ]),
                campo_monto,
                ft.Divider(),
                ft.Row(controls=[
                    boton("Cancelar", lambda e: page.pop_dialog(), color=ft.Colors.GREY_400, expand=True),
                    boton("Guardar", guardar_fiado, color=ft.Colors.BLUE_700, expand=True),
                ], spacing=10),
            ], spacing=15, scroll=ft.ScrollMode.AUTO),
            bgcolor=ft.Colors.WHITE, padding=20, border_radius=15, width=ancho_dialogo(), height=650
        )
        page.show_dialog(ft.AlertDialog(content=contenido, actions=[]))

    # =========================================================
    # PANTALLA DE VENTAS (FILTRADO POR MES ACTUAL)
    # =========================================================
    def abrir_ventas(e):
        page.controls.clear()
        page.bottom_appbar = None
        
        mes_actual = datetime.now().strftime("%m/%Y")
        ventas_mes = [v for v in ventas if v["fecha"].split(" ")[0].endswith(mes_actual)]
        total_mes = sum(v["monto"] for v in ventas_mes)

        def lista_ventas():
            if not ventas_mes: 
                return ft.Text("No hay ventas registradas este mes.", color=ft.Colors.GREY_600)
            
            filas = []
            for v in reversed(ventas_mes):
                filas.append(ft.Container(content=ft.Row(controls=[
                    ft.Icon(ft.Icons.SHOPPING_BAG, color=ft.Colors.BLUE_500),
                    ft.Column(controls=[ft.Text(v["descripcion"], weight=ft.FontWeight.BOLD), ft.Text(f"{v['fecha']} | {v['medio']}", size=11)], expand=True),
                    ft.Text(formatear_monto(v["monto"]), weight=ft.FontWeight.BOLD)
                ]), padding=15, bgcolor=ft.Colors.WHITE, border_radius=10, margin=ft.Margin.only(bottom=8)))
            return ft.Column(controls=filas)

        btn_nueva_venta = ft.Container(
            content=ft.Row(controls=[
                ft.Icon(ft.Icons.ADD, color=ft.Colors.WHITE), 
                ft.Text("Registrar Nueva Venta", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
            ], alignment=ft.MainAxisAlignment.CENTER),
            bgcolor=ft.Colors.BLUE_700, padding=15, border_radius=10, margin=ft.Margin.only(bottom=20),
            on_click=lambda e: formulario_nueva_venta(None), ink=True
        )

        page.add(ft.Column(controls=[
            ft.Container(content=ft.Text(f"Ventas de {mes_actual}", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900), padding=ft.Padding.only(left=20, top=20)),
            ft.Container(content=ft.Column([ft.Text("Total del mes"), ft.Text(formatear_monto(total_mes), size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900)]), bgcolor=ft.Colors.WHITE, padding=20, border_radius=15, margin=20),
            ft.Container(content=btn_nueva_venta, padding=ft.Padding.only(left=20, right=20)),
            ft.Container(content=lista_ventas(), padding=ft.Padding.only(left=20, right=20))
        ], scroll=ft.ScrollMode.AUTO, expand=True))
        
        page.bottom_appbar = crear_bottom_appbar(3)
        page.update()

    def formulario_nueva_venta(e):
        campo_descripcion = campo_texto("¿Qué se vendió?", hint_text="Ej: Servicio, Producto no registrado...")
        campo_monto_manual = campo_texto(f"Monto manual ({moneda_actual})", keyboard_type=ft.KeyboardType.NUMBER)
        campo_total = ft.TextField(label="Total a cobrar", read_only=True, value="0.00", border=ft.OutlineInputBorder(side=ft.BorderSide(1, ft.Colors.BLUE_300), border_radius=10))
        campo_medio_pago = ft.Dropdown(
            label="Medio de pago", value="Efectivo",
            options=[ft.dropdown.Option(m) for m in ["Efectivo", "Divisa", "Punto de Venta", "Pago Móvil", "Transferencia", "Otro"]],
            border=ft.OutlineInputBorder(side=ft.BorderSide(1, ft.Colors.BLUE_300), border_radius=10)
        )
        
        productos_seleccionados = []
        texto_resumen = ft.Text("No has seleccionado productos del inventario", size=12, color=ft.Colors.GREY_600)

        def actualizar_vista():
            total_inventario = sum(item["precio"] * item["cant"] for item in productos_seleccionados)
            try: monto_manual = float(campo_monto_manual.value.replace(",", ".")) if campo_monto_manual.value else 0.0
            except ValueError: monto_manual = 0.0

            total_final = monto_manual + total_inventario
            campo_total.value = f"{total_final:.2f}"
            
            if productos_seleccionados:
                resumen = ", ".join([f"{p['cant']}x {p['nombre']}" for p in productos_seleccionados])
                texto_resumen.value = f"Inventario: {resumen}"
            else:
                texto_resumen.value = "No has seleccionado productos del inventario"
            page.update()

        campo_monto_manual.on_change = lambda e: actualizar_vista()

        def abrir_selector_productos(e):
            if not productos:
                page.show_dialog(ft.AlertDialog(title=ft.Text("Inventario vacío"), content=ft.Text("No hay productos registrados.")))
                return

            def seleccionar(index):
                p = productos[index]
                if p["stock"] <= 0: return
                
                existente = next((item for item in productos_seleccionados if item["nombre"] == p["nombre"]), None)
                if existente: existente["cant"] += 1
                else: productos_seleccionados.append({"nombre": p["nombre"], "precio": p["precio"], "cant": 1, "index": index})
                
                p["stock"] -= 1
                actualizar_vista()
                page.pop_dialog()
                
            filas = [ft.Container(content=ft.Row([ft.Text(p["nombre"], expand=True), ft.Text(f"Stock: {p['stock']} | {formatear_monto(p['precio'])}"), ft.IconButton(ft.Icons.ADD, on_click=lambda e, i=i: seleccionar(i))])) for i, p in enumerate(productos) if p["stock"] > 0]
            
            page.show_dialog(ft.AlertDialog(
                title=ft.Text("Seleccionar Producto"),
                content=ft.Column(filas, height=300, scroll=ft.ScrollMode.AUTO) if filas else ft.Text("No hay stock disponible"),
                actions=[boton("Cerrar", lambda e: page.pop_dialog(), color=ft.Colors.GREY_400)]
            ))

        def guardar_venta(e):
            try: monto_manual = float(campo_monto_manual.value.replace(",", ".")) if campo_monto_manual.value else 0.0
            except ValueError: campo_monto_manual.error_text = "Inválido"; page.update(); return

            total_inventario = sum(item["precio"] * item["cant"] for item in productos_seleccionados)
            total_final = monto_manual + total_inventario

            if total_final <= 0:
                page.show_dialog(ft.AlertDialog(title=ft.Text("Error"), content=ft.Text("El total debe ser mayor a 0.")))
                return

            desc_partes = []
            if campo_descripcion.value.strip(): desc_partes.append(campo_descripcion.value.strip())
            if productos_seleccionados:
                resumen_inv = ", ".join([f"{p['cant']}x {p['nombre']}" for p in productos_seleccionados])
                desc_partes.append(resumen_inv)
            
            descripcion_final = " + ".join(desc_partes) if desc_partes else "Venta Varios"

            ventas.append({
                "monto": total_final, "descripcion": descripcion_final,
                "medio": campo_medio_pago.value, "fecha": datetime.now().strftime("%d/%m/%Y %H:%M")
            })
            
            guardar_datos(fiados, ventas, productos)
            page.pop_dialog() 
            abrir_ventas(None)

        contenido = ft.Container(
            content=ft.Column(controls=[
                ft.Text("Registrar Venta", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900), 
                ft.Divider(), 
                ft.Text("1. Venta Libre / Servicio", weight=ft.FontWeight.BOLD, size=14),
                campo_descripcion,
                campo_monto_manual,
                ft.Text("2. Vender del Inventario (Opcional)", weight=ft.FontWeight.BOLD, size=14),
                ft.Row(controls=[
                    texto_resumen,
                    ft.Button("Añadir Producto", on_click=abrir_selector_productos, bgcolor=ft.Colors.BLUE_500, color=ft.Colors.WHITE)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(),
                campo_total,
                campo_medio_pago,
                ft.Divider(),
                ft.Row(controls=[
                    boton("Cancelar", lambda e: page.pop_dialog(), color=ft.Colors.GREY_400, expand=True),
                    boton("Cobrar y Guardar", guardar_venta, color=ft.Colors.BLUE_700, expand=True),
                ], spacing=10),
            ], spacing=15, scroll=ft.ScrollMode.AUTO),
            bgcolor=ft.Colors.WHITE, padding=20, border_radius=15, width=ancho_dialogo(), height=650
        )
        page.show_dialog(ft.AlertDialog(content=contenido, actions=[]))

    # =========================================================
    # INVENTARIO
    # =========================================================
    def abrir_inventario(e):
        page.controls.clear(); page.bottom_appbar = None
        
        def agregar(e):
            nom = campo_texto("Nombre"); costo = campo_texto("Costo"); prec = campo_texto("Precio"); st = campo_texto("Stock", value="0")
            def g(e):
                try:
                    productos.append({"nombre": nom.value, "costo": float(costo.value), "precio": float(prec.value), "stock": int(st.value)})
                    guardar_datos(fiados, ventas, productos); page.pop_dialog(); abrir_inventario(None)
                except: pass
            page.show_dialog(ft.AlertDialog(title=ft.Text("Agregar"), content=ft.Column([nom, costo, prec, st]), actions=[boton("Guardar", g)]))

        filas = [ft.Container(content=ft.Row([ft.Column([ft.Text(p["nombre"], weight=ft.FontWeight.BOLD), ft.Text(f"Stock: {p['stock']} | Precio: {formatear_monto(p['precio'])}")], expand=True), ft.IconButton(ft.Icons.DELETE, on_click=lambda e, i=i: (productos.pop(i), guardar_datos(fiados, ventas, productos), abrir_inventario(None)))]), padding=15, bgcolor=ft.Colors.WHITE, margin=ft.Margin.only(bottom=8), border_radius=10) for i, p in enumerate(productos)]
        
        page.add(ft.Column([
            ft.Row([ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: mostrar_app_principal()), ft.Text("Inventario", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900), ft.IconButton(ft.Icons.ADD, icon_color=ft.Colors.BLUE_700, on_click=agregar)]),
            ft.Container(content=ft.Column(filas), padding=20)
        ], scroll=ft.ScrollMode.AUTO, expand=True))
        page.update()

    # =========================================================
    # AJUSTES DEL NEGOCIO
    # =========================================================
    def abrir_ajustes(e):
        campo_nombre = campo_texto("Nombre del negocio", value=datos_negocio["nombre"])
        campo_tipo = ft.Dropdown(
            label="Tipo de negocio", value=datos_negocio["tipo"],
            options=[ft.dropdown.Option(t) for t in
                     ["Bodega", "Frutería", "Servicio Técnico", "Panadería", "Farmacia", "Ferretería", "Otro"]],
            border=ft.OutlineInputBorder(side=ft.BorderSide(1, ft.Colors.BLUE_300), border_radius=10)
        )
        campo_telefono = campo_texto("Teléfono del negocio", value=datos_negocio["telefono"])
        campo_direccion = campo_texto("Dirección", value=datos_negocio["direccion"], multiline=True, min_lines=2, max_lines=3)
        campo_moneda = ft.Dropdown(
            label="Moneda", value=moneda_actual,
            options=[
                ft.dropdown.Option("Bs.", "Bolívares (Bs.)"),
                ft.dropdown.Option("USD$", "Dólares (USD$)"),
            ],
            border=ft.OutlineInputBorder(side=ft.BorderSide(1, ft.Colors.BLUE_300), border_radius=10)
        )

        def guardar(e):
            nonlocal moneda_actual
            datos_negocio["nombre"] = campo_nombre.value or "Mi Negocio"
            datos_negocio["tipo"] = campo_tipo.value or "Bodega"
            datos_negocio["telefono"] = campo_telefono.value or ""
            datos_negocio["direccion"] = campo_direccion.value or ""
            moneda_actual = campo_moneda.value or "Bs."
            
            config["negocio"] = datos_negocio
            config["moneda"] = moneda_actual
            guardar_config(config)
            
            page.pop_dialog()
            mostrar_app_principal()

        contenido = ft.Container(
            content=ft.Column(controls=[
                ft.Row(controls=[
                    ft.Container(content=ft.Icon(ft.Icons.STORE, color=ft.Colors.WHITE, size=26),
                                 bgcolor=ft.Colors.BLUE_700, padding=10, border_radius=50),
                    ft.Text("Datos del Negocio", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900, expand=True),
                ], spacing=10),
                ft.Divider(),
                campo_nombre, campo_tipo, campo_telefono, campo_direccion, campo_moneda,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                ft.Row(controls=[
                    boton("Cancelar", lambda e: page.pop_dialog(), color=ft.Colors.GREY_400, expand=True),
                    boton("Guardar", guardar, color=ft.Colors.BLUE_700, expand=True),
                ], spacing=8),
            ], spacing=10, scroll=ft.ScrollMode.AUTO),
            bgcolor=ft.Colors.WHITE, padding=20, border_radius=20,
            width=ancho_dialogo(),
            height=min(page.height * 0.85 if page.height else 600, 700),
        )
        page.show_dialog(ft.AlertDialog(content=contenido, actions=[]))

    # =========================================================
    # MENÚ
    # =========================================================
    def abrir_menu(e):
        def item_menu(icono, titulo, accion):
            return ft.Container(
                content=ft.Row(controls=[
                    ft.Icon(icono, color=ft.Colors.BLUE_700, size=24), 
                    ft.Text(titulo, size=15, weight=ft.FontWeight.BOLD, expand=True)
                ]),
                padding=15, bgcolor=ft.Colors.BLUE_50, border_radius=10, on_click=accion, ink=True,
                margin=ft.Margin.only(bottom=8)
            )
            
        contenido = ft.Container(
            content=ft.Column(controls=[
                ft.Row(controls=[
                    ft.Container(content=ft.Icon(ft.Icons.MENU, color=ft.Colors.WHITE, size=26),
                                 bgcolor=ft.Colors.BLUE_700, padding=10, border_radius=50),
                    ft.Text("Menú Principal", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900, expand=True),
                ], spacing=10),
                ft.Divider(),
                item_menu(ft.Icons.INVENTORY, "Inventario", lambda e: (page.pop_dialog(), abrir_inventario(None))),
                item_menu(ft.Icons.STORE, "Ajustes del Negocio", lambda e: (page.pop_dialog(), abrir_ajustes(None))),
                ft.Container(height=10),
                boton("Cerrar", lambda e: page.pop_dialog(), color=ft.Colors.GREY_400)
            ], spacing=10), 
            bgcolor=ft.Colors.WHITE, padding=20, border_radius=15, width=ancho_dialogo()
        )
        page.show_dialog(ft.AlertDialog(content=contenido, actions=[]))

    # Iniciar
    mostrar_app_principal()

ft.run(main)
