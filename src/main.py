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
    page.scroll = ft.ScrollMode.AUTO
    page.bgcolor = ft.Colors.PINK_50

    # ====== CARGAR DATOS GUARDADOS ======
    config = cargar_config()
    datos_negocio = config["negocio"]
    pin_guardado = config.get("pin")
    moneda_actual = config.get("moneda", "Bs.")

    fiados, ventas, productos = cargar_datos()

    # ====== HELPERS ======
    def ancho_dialogo():
        ancho_pantalla = page.width if page.width else 400
        return min(ancho_pantalla - 30, 500)

    def borde_naranja():
        return ft.OutlineInputBorder(side=ft.BorderSide(2, ft.Colors.ORANGE_400), border_radius=10)
    def borde_rosa():
        return ft.OutlineInputBorder(side=ft.BorderSide(2, ft.Colors.PINK_300), border_radius=10)
    def borde_verde():
        return ft.OutlineInputBorder(side=ft.BorderSide(2, ft.Colors.GREEN_400), border_radius=10)
    def borde_azul():
        return ft.OutlineInputBorder(side=ft.BorderSide(2, ft.Colors.BLUE_400), border_radius=10)

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
            if fiados:
                texto_subtitulo_total.value = f"{len(fiados)} fiado(s) pendiente(s)"
            else:
                texto_subtitulo_total.value = "Tu cartera está al día ✨"
            page.update()
        except Exception:
            pass

    def mostrar_mensaje_copiable(titulo, mensaje):
        async def copiar(e):
            try:
                await ft.Clipboard().set(mensaje)
            except Exception:
                pass
            page.pop_dialog()
            page.show_dialog(ft.AlertDialog(
                content=ft.Text("✅ Mensaje copiado al portapapeles"),
                actions=[ft.Button("OK", on_click=lambda e: page.pop_dialog())],
            ))
        page.show_dialog(ft.AlertDialog(
            title=ft.Text(titulo),
            content=ft.Text(mensaje, selectable=True),
            actions=[
                ft.Button("📋 Copiar", on_click=copiar, bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE),
                ft.Button("Cerrar", on_click=lambda e: page.pop_dialog()),
            ],
        ))

    # =========================================================
    # AJUSTES
    # =========================================================
    def abrir_ajustes(e):
        campo_nombre = ft.TextField(label="Nombre del negocio", value=datos_negocio["nombre"], border=borde_naranja())
        campo_tipo = ft.Dropdown(
            label="Tipo de negocio", value=datos_negocio["tipo"],
            options=[ft.dropdown.Option(t) for t in
                     ["Bodega", "Frutería", "Servicio Técnico", "Panadería", "Farmacia", "Ferretería", "Otro"]],
            border_color=ft.Colors.ORANGE_400,
        )
        campo_telefono = ft.TextField(label="Teléfono del negocio", value=datos_negocio["telefono"], border=borde_naranja())
        campo_direccion = ft.TextField(label="Dirección", value=datos_negocio["direccion"],
                                       multiline=True, min_lines=2, max_lines=3, border=borde_naranja())
        campo_moneda = ft.Dropdown(
            label="Moneda", value=moneda_actual,
            options=[
                ft.dropdown.Option("Bs.", "Bolívares (Bs.)"),
                ft.dropdown.Option("USD$", "Dólares (USD$)"),
            ],
            border_color=ft.Colors.ORANGE_400,
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
                                 bgcolor=ft.Colors.ORANGE_700, padding=10, border_radius=50),
                    ft.Text("Datos del Negocio", size=18, weight=ft.FontWeight.BOLD, expand=True),
                ], spacing=10),
                ft.Divider(),
                campo_nombre, campo_tipo, campo_telefono, campo_direccion, campo_moneda,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                ft.Row(controls=[
                    ft.Button("Cancelar", on_click=lambda e: page.pop_dialog(), expand=True),
                    ft.Button("Guardar", on_click=guardar, bgcolor=ft.Colors.ORANGE_700,
                              color=ft.Colors.WHITE, expand=True),
                ], spacing=8),
            ], spacing=10, scroll=ft.ScrollMode.AUTO),
            bgcolor=ft.Colors.WHITE, padding=20, border_radius=20,
            width=ancho_dialogo(),
            height=min(page.height * 0.85 if page.height else 600, 700),
            shadow=ft.BoxShadow(blur_radius=20, color=ft.Colors.with_opacity(0.3, ft.Colors.ORANGE_700)),
        )
        page.show_dialog(ft.AlertDialog(content=contenido, actions=[]))

    # =========================================================
    # INVENTARIO
    # =========================================================
    def abrir_inventario(e):
        page.controls.clear()
        
        def agregar_producto(e):
            campo_nombre = ft.TextField(label="Nombre del producto", border=borde_naranja())
            campo_costo = ft.TextField(label="Costo", keyboard_type=ft.KeyboardType.NUMBER, border=borde_naranja())
            campo_precio = ft.TextField(label="Precio de venta", keyboard_type=ft.KeyboardType.NUMBER, border=borde_naranja())
            campo_stock = ft.TextField(label="Stock", value="0", keyboard_type=ft.KeyboardType.NUMBER, border=borde_naranja())

            def guardar(e):
                try:
                    nombre = campo_nombre.value.strip()
                    costo = float(campo_costo.value.replace(",", ".")) if campo_costo.value else 0.0
                    precio = float(campo_precio.value.replace(",", ".")) if campo_precio.value else 0.0
                    stock = int(campo_stock.value) if campo_stock.value else 0
                    
                    if not nombre:
                        campo_nombre.error_text = "Obligatorio"
                        page.update()
                        return
                        
                    productos.append({
                        "nombre": nombre, "costo": costo, "precio": precio, "stock": stock
                    })
                    guardar_datos(fiados, ventas, productos)
                    page.pop_dialog()
                    abrir_inventario(None)
                except ValueError:
                    page.show_dialog(ft.AlertDialog(title=ft.Text("Error"), content=ft.Text("Valores numéricos inválidos")))

            contenido = ft.Container(
                content=ft.Column(controls=[
                    ft.Text("Agregar Producto", size=18, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    campo_nombre, campo_costo, campo_precio, campo_stock,
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    ft.Row(controls=[
                        ft.Button("Cancelar", on_click=lambda e: page.pop_dialog(), expand=True),
                        ft.Button("Guardar", on_click=guardar, bgcolor=ft.Colors.ORANGE_700, color=ft.Colors.WHITE, expand=True),
                    ], spacing=8),
                ], spacing=10),
                bgcolor=ft.Colors.WHITE, padding=20, border_radius=20, width=ancho_dialogo(),
            )
            page.show_dialog(ft.AlertDialog(content=contenido, actions=[]))

        def eliminar_producto(index):
            def confirmar(e):
                productos.pop(index)
                guardar_datos(fiados, ventas, productos)
                page.pop_dialog()
                abrir_inventario(None)
            
            page.show_dialog(ft.AlertDialog(
                title=ft.Text("Eliminar producto"),
                content=ft.Text("¿Estás seguro de eliminar este producto?"),
                actions=[
                    ft.Button("Cancelar", on_click=lambda e: page.pop_dialog()),
                    ft.Button("Eliminar", on_click=confirmar, bgcolor=ft.Colors.RED_600, color=ft.Colors.WHITE),
                ]
            ))

        filas = []
        if not productos:
            filas.append(ft.Text("No hay productos en el inventario", color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER))
        else:
            for i, p in enumerate(productos):
                filas.append(
                    ft.Container(
                        content=ft.Row(controls=[
                            ft.Column(controls=[
                                ft.Text(p["nombre"], weight=ft.FontWeight.BOLD, size=15),
                                ft.Text(f"Stock: {p['stock']} | Costo: {formatear_monto(p['costo'])} | Venta: {formatear_monto(p['precio'])}", size=11, color=ft.Colors.GREY_600),
                            ], spacing=2, expand=True),
                            ft.IconButton(ft.Icons.DELETE, icon_color=ft.Colors.RED_600, on_click=lambda e, idx=i: eliminar_producto(idx)),
                        ]),
                        bgcolor=ft.Colors.WHITE, padding=12, border_radius=10,
                        margin=ft.Margin.only(bottom=8),
                        border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_200), bottom=ft.BorderSide(1, ft.Colors.GREY_200), left=ft.BorderSide(1, ft.Colors.GREY_200), right=ft.BorderSide(1, ft.Colors.GREY_200)),
                    )
                )

        encabezado = ft.Container(
            content=ft.Row(controls=[
                ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: mostrar_app_principal()),
                ft.Text("Inventario", size=24, weight=ft.FontWeight.BOLD, expand=True),
                ft.IconButton(ft.Icons.ADD_CIRCLE, icon_color=ft.Colors.ORANGE_700, icon_size=30, on_click=agregar_producto),
            ]), padding=20
        )

        contenido = ft.Column(
            controls=[
                encabezado,
                ft.Container(content=ft.Column(controls=filas), padding=ft.Padding.only(left=20, right=20)),
            ], scroll=ft.ScrollMode.AUTO, expand=True
        )
        
        page.add(contenido)
        page.update()

    # =========================================================
    # REGISTRAR FIADO
    # =========================================================
    def abrir_registrar_fiado(e):
        campo_cliente = ft.TextField(label="Nombre del cliente", border=borde_rosa(), prefix_icon=ft.Icons.PERSON)
        campo_telefono_cliente = ft.TextField(label="Teléfono del cliente", border=borde_rosa(), prefix_icon=ft.Icons.PHONE)
        campo_monto = ft.TextField(label=f"Monto ({moneda_actual})", hint_text="Ej: 4.500,50",
                                   border=borde_rosa(), prefix_icon=ft.Icons.ATTACH_MONEY)
        campo_fecha = ft.TextField(label="Fecha de pago", hint_text="Ej: 15/11/2026",
                                   border=borde_rosa(), prefix_icon=ft.Icons.CALENDAR_MONTH)
        campo_descripcion = ft.TextField(label="Descripción", hint_text="Ej: 2 harinas", multiline=True,
                                         min_lines=2, max_lines=3, border=borde_rosa(), prefix_icon=ft.Icons.SHOPPING_BAG)

        def guardar_fiado(e):
            nombre = campo_cliente.value.strip()
            telefono = campo_telefono_cliente.value.strip()
            monto = campo_monto.value.strip()
            fecha = campo_fecha.value.strip()
            descripcion = campo_descripcion.value.strip()

            if not nombre or not monto:
                campo_cliente.error_text = "Obligatorio" if not nombre else None
                campo_monto.error_text = "Obligatorio" if not monto else None
                page.update()
                return
            try:
                monto_limpio = monto.replace(".", "").replace(",", ".")
                monto_float = float(monto_limpio)
            except ValueError:
                campo_monto.error_text = "Monto inválido"
                page.update()
                return

            fiados.append({
                "cliente": nombre, "telefono": telefono, "monto": monto_float,
                "monto_original": monto_float, "abonado": 0.0,
                "fecha_pago": fecha, "descripcion": descripcion,
            })
            
            guardar_datos(fiados, ventas, productos)
            refrescar_totales()
            page.pop_dialog()

        contenido = ft.Container(
            content=ft.Column(controls=[
                ft.Row(controls=[
                    ft.Container(content=ft.Icon(ft.Icons.ADD_CIRCLE, color=ft.Colors.WHITE, size=26),
                                 bgcolor=ft.Colors.PINK_700, padding=10, border_radius=50),
                    ft.Text("Registrar Fiado", size=18, weight=ft.FontWeight.BOLD, expand=True),
                ], spacing=10),
                ft.Divider(),
                campo_cliente, campo_telefono_cliente, campo_monto, campo_fecha, campo_descripcion,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                ft.Row(controls=[
                    ft.Button("Cancelar", on_click=lambda e: page.pop_dialog(), expand=True),
                    ft.Button("Guardar", on_click=guardar_fiado, bgcolor=ft.Colors.PINK_700,
                              color=ft.Colors.WHITE, expand=True),
                ], spacing=8),
            ], spacing=10, scroll=ft.ScrollMode.AUTO),
            bgcolor=ft.Colors.WHITE, padding=20, border_radius=20,
            width=ancho_dialogo(),
            height=min(page.height * 0.85 if page.height else 600, 650),
            shadow=ft.BoxShadow(blur_radius=20, color=ft.Colors.with_opacity(0.3, ft.Colors.PINK_700)),
        )
        page.show_dialog(ft.AlertDialog(content=contenido, actions=[]))

    # =========================================================
    # EDITAR FECHA
    # =========================================================
    def editar_fecha(fiado):
        campo_nueva_fecha = ft.TextField(label="Nueva fecha de pago", value=fiado["fecha_pago"],
                                         border=borde_azul(), prefix_icon=ft.Icons.CALENDAR_MONTH)

        def guardar(e):
            fiado["fecha_pago"] = campo_nueva_fecha.value.strip()
            guardar_datos(fiados, ventas, productos) 
            page.pop_dialog()
            page.pop_dialog()
            abrir_cartera(None)

        contenido = ft.Container(
            content=ft.Column(controls=[
                ft.Row(controls=[
                    ft.Container(content=ft.Icon(ft.Icons.EDIT_CALENDAR, color=ft.Colors.WHITE, size=26),
                                 bgcolor=ft.Colors.BLUE_600, padding=10, border_radius=50),
                    ft.Text("Editar fecha", size=18, weight=ft.FontWeight.BOLD, expand=True),
                ], spacing=10),
                ft.Divider(),
                ft.Text(f"Cliente: {fiado['cliente']}", size=14, weight=ft.FontWeight.BOLD),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                campo_nueva_fecha,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                ft.Row(controls=[
                    ft.Button("Cancelar", on_click=lambda e: page.pop_dialog(), expand=True),
                    ft.Button("Guardar", on_click=guardar, bgcolor=ft.Colors.BLUE_600,
                              color=ft.Colors.WHITE, expand=True),
                ], spacing=8),
            ], spacing=10),
            bgcolor=ft.Colors.WHITE, padding=20, border_radius=20,
            width=ancho_dialogo(),
            shadow=ft.BoxShadow(blur_radius=20, color=ft.Colors.with_opacity(0.3, ft.Colors.BLUE_600)),
        )
        page.show_dialog(ft.AlertDialog(content=contenido, actions=[]))

    # =========================================================
    # REGISTRAR ABONO
    # =========================================================
    def registrar_abono(fiado):
        campo_abono = ft.TextField(label=f"Monto del abono ({moneda_actual})", hint_text="Ej: 1.000,00",
                                   border=borde_verde(), prefix_icon=ft.Icons.ATTACH_MONEY)

        def guardar(e):
            abono_str = campo_abono.value.strip()
            if not abono_str:
                campo_abono.error_text = "Obligatorio"
                page.update()
                return
            try:
                abono_limpio = abono_str.replace(".", "").replace(",", ".")
                abono_float = float(abono_limpio)
            except ValueError:
                campo_abono.error_text = "Monto inválido"
                page.update()
                return
            if abono_float <= 0:
                campo_abono.error_text = "Debe ser mayor a 0"
                page.update()
                return
            if abono_float > fiado["monto"]:
                campo_abono.error_text = "Excede el saldo"
                page.update()
                return

            fiado["abonado"] = fiado.get("abonado", 0.0) + abono_float
            fiado["monto"] = fiado["monto"] - abono_float

            if fiado["monto"] <= 0.01:
                if fiado in fiados:
                    fiados.remove(fiado)
                guardar_datos(fiados, ventas, productos) 
                page.pop_dialog()
                page.pop_dialog()
                refrescar_totales()
                return

            guardar_datos(fiados, ventas, productos) 
            page.pop_dialog()
            page.pop_dialog()
            refrescar_totales()
            abrir_cartera(None)

        contenido = ft.Container(
            content=ft.Column(controls=[
                ft.Row(controls=[
                    ft.Container(content=ft.Icon(ft.Icons.PAYMENTS, color=ft.Colors.WHITE, size=26),
                                 bgcolor=ft.Colors.GREEN_600, padding=10, border_radius=50),
                    ft.Text("Registrar abono", size=18, weight=ft.FontWeight.BOLD, expand=True),
                ], spacing=10),
                ft.Divider(),
                ft.Text(f"Cliente: {fiado['cliente']}", size=14, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.Column(controls=[
                        ft.Text(f"Saldo pendiente: {formatear_monto(fiado['monto'])}",
                                size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_700),
                    ], spacing=3),
                    bgcolor=ft.Colors.GREY_100, padding=12, border_radius=10,
                ),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                campo_abono,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                ft.Row(controls=[
                    ft.Button("Cancelar", on_click=lambda e: page.pop_dialog(), expand=True),
                    ft.Button("Abonar", on_click=guardar, bgcolor=ft.Colors.GREEN_600,
                              color=ft.Colors.WHITE, expand=True),
                ], spacing=8),
            ], spacing=10),
            bgcolor=ft.Colors.WHITE, padding=20, border_radius=20,
            width=ancho_dialogo(),
            shadow=ft.BoxShadow(blur_radius=20, color=ft.Colors.with_opacity(0.3, ft.Colors.GREEN_600)),
        )
        page.show_dialog(ft.AlertDialog(content=contenido, actions=[]))

    # =========================================================
    # ELIMINAR FIADO
    # =========================================================
    def eliminar_fiado(fiado):
        def confirmar(e):
            if fiado in fiados:
                fiados.remove(fiado)
            guardar_datos(fiados, ventas, productos)
            refrescar_totales()
            page.pop_dialog()
            page.pop_dialog()
            abrir_cartera(None)

        contenido = ft.Container(
            content=ft.Column(controls=[
                ft.Row(controls=[
                    ft.Container(content=ft.Icon(ft.Icons.DELETE, color=ft.Colors.WHITE, size=26),
                                 bgcolor=ft.Colors.RED_600, padding=10, border_radius=50),
                    ft.Text("Eliminar fiado", size=17, weight=ft.FontWeight.BOLD, expand=True),
                ], spacing=10),
                ft.Divider(),
                ft.Text(f"Cliente: {fiado['cliente']}", size=14),
                ft.Text(f"Monto: {formatear_monto(fiado['monto'])}", size=14, color=ft.Colors.ORANGE_700),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                ft.Text("¿Eliminar este fiado porque ya pagó?", size=14, color=ft.Colors.GREY_700),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                ft.Row(controls=[
                    ft.Button("Cancelar", on_click=lambda e: page.pop_dialog(), expand=True),
                    ft.Button("Eliminar", on_click=confirmar, bgcolor=ft.Colors.RED_600,
                              color=ft.Colors.WHITE, expand=True),
                ], spacing=8),
            ], spacing=10),
            bgcolor=ft.Colors.WHITE, padding=20, border_radius=20,
            width=ancho_dialogo(),
            shadow=ft.BoxShadow(blur_radius=20, color=ft.Colors.with_opacity(0.3, ft.Colors.RED_600)),
        )
        page.show_dialog(ft.AlertDialog(content=contenido, actions=[]))

    # =========================================================
    # VER CARTERA
    # =========================================================
    def abrir_cartera(e):
        if not fiados:
            contenido_lista = ft.Container(
                content=ft.Column(controls=[
                    ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN_400, size=60),
                    ft.Text("Aún no hay fiados registrados", size=15,
                            weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_700, text_align=ft.TextAlign.CENTER),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                padding=30,
            )
        else:
            filas = []
            for f in fiados:
                def crear_recordatorio(fiado=f):
                    def recordar(e):
                        msg = (f"Hola {fiado['cliente']}, le saluda {datos_negocio['nombre']}. "
                               f"Le recordamos que tiene un saldo pendiente de {formatear_monto(fiado['monto'])}")
                        if fiado.get('fecha_pago'):
                            msg += f" con fecha de pago para el {fiado['fecha_pago']}"
                        msg += ". Agradecemos su pronto pago. ¡Gracias!"
                        if fiado.get('telefono'):
                            try: abrir_whatsapp(fiado['telefono'], msg)
                            except Exception: mostrar_mensaje_copiable("Mensaje", msg)
                        else: mostrar_mensaje_copiable("Mensaje", msg)
                    return recordar

                filas.append(ft.Container(
                    content=ft.Column(controls=[
                        ft.Row(controls=[
                            ft.Container(content=ft.Icon(ft.Icons.PERSON, color=ft.Colors.WHITE, size=18),
                                         bgcolor=ft.Colors.ORANGE_400, padding=8, border_radius=50),
                            ft.Column(controls=[
                                ft.Text(f["cliente"], weight=ft.FontWeight.BOLD, size=14),
                                ft.Text(f["descripcion"] or "(sin descripción)", size=11, color=ft.Colors.GREY_600),
                            ], spacing=2, expand=True),
                            ft.Text(formatear_monto(f["monto"]), weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.ORANGE_700, size=15),
                        ]),
                        ft.Text(f"📅 {f['fecha_pago'] or 'Sin fecha'}  |  📞 {f['telefono'] or 'Sin teléfono'}",
                                size=11, color=ft.Colors.GREY_500),
                        
                        ft.Row(controls=[
                            ft.Button("💬 Recordar", on_click=crear_recordatorio(f),
                                      bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE, expand=True),
                            ft.Button("💵 Abono", on_click=lambda e, fiado=f: registrar_abono(fiado),
                                      bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE, expand=True),
                        ], spacing=6),
                        
                        ft.Row(controls=[
                            ft.Button("📅 Fecha", on_click=lambda e, fiado=f: editar_fecha(fiado),
                                      bgcolor=ft.Colors.ORANGE_600, color=ft.Colors.WHITE, expand=True),
                            ft.Button("🗑️ Eliminar", on_click=lambda e, fiado=f: eliminar_fiado(fiado),
                                      bgcolor=ft.Colors.RED_600, color=ft.Colors.WHITE, expand=True),
                        ], spacing=6),
                    ], spacing=8),
                    bgcolor=ft.Colors.WHITE, padding=12, border_radius=15,
                    margin=ft.Margin.only(bottom=10),
                    shadow=ft.BoxShadow(blur_radius=6, color=ft.Colors.with_opacity(0.12, ft.Colors.BLACK)),
                ))
            contenido_lista = ft.Column(controls=filas, spacing=5)

        total = sum(f["monto"] for f in fiados)

        contenido = ft.Container(
            content=ft.Column(controls=[
                ft.Row(controls=[
                    ft.Container(content=ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET, color=ft.Colors.WHITE, size=24),
                                 bgcolor=ft.Colors.ORANGE_700, padding=10, border_radius=50),
                    ft.Column(controls=[
                        ft.Text("Cartera por cobrar", size=17, weight=ft.FontWeight.BOLD),
                        ft.Text(f"Total: {formatear_monto(total)}", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_700),
                    ], spacing=2, expand=True),
                ], spacing=10),
                ft.Divider(),
                contenido_lista,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                ft.Row(controls=[
                    ft.Button("Cerrar", on_click=lambda e: page.pop_dialog(),
                              bgcolor=ft.Colors.ORANGE_700, color=ft.Colors.WHITE, expand=True),
                ]),
            ], spacing=10, scroll=ft.ScrollMode.AUTO),
            bgcolor=ft.Colors.WHITE, padding=15, border_radius=20,
            width=ancho_dialogo(),
            height=min(page.height * 0.9 if page.height else 600, 700),
            shadow=ft.BoxShadow(blur_radius=20, color=ft.Colors.with_opacity(0.3, ft.Colors.ORANGE_700)),
        )
        page.show_dialog(ft.AlertDialog(content=contenido, actions=[]))

    # =========================================================
    # REGISTRAR VENTA (CONECTADO AL INVENTARIO)
    # =========================================================
    def abrir_registrar_venta(e):
        if not productos:
            page.show_dialog(ft.AlertDialog(title=ft.Text("Inventario vacío"), content=ft.Text("Primero debes agregar productos en el menú de Inventario.")))
            return

        def vender_producto(index):
            p = productos[index]
            if p["stock"] <= 0:
                page.show_dialog(ft.AlertDialog(title=ft.Text("Sin stock"), content=ft.Text("No tienes stock de este producto.")))
                return

            campo_cantidad = ft.TextField(label="Cantidad a vender", value="1", keyboard_type=ft.KeyboardType.NUMBER)
            campo_medio = ft.Dropdown(label="Medio de pago", value="Efectivo",
                options=[ft.dropdown.Option(m) for m in ["Efectivo", "Pago Móvil", "Transferencia", "Punto", "Otro"]])

            def confirmar_venta(e):
                try:
                    cant = int(campo_cantidad.value)
                    if cant <= 0 or cant > p["stock"]:
                        campo_cantidad.error_text = "Cantidad inválida"
                        page.update()
                        return
                    
                    total = cant * p["precio"]
                    
                    ventas.append({
                        "monto": total, "descripcion": f"{cant}x {p['nombre']}",
                        "medio": campo_medio.value, "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    })
                    
                    productos[index]["stock"] -= cant
                    
                    guardar_datos(fiados, ventas, productos)
                    page.pop_dialog()
                    page.pop_dialog()
                    abrir_ventas(None)
                except ValueError:
                    campo_cantidad.error_text = "Número inválido"
                    page.update()

            contenido = ft.Container(
                content=ft.Column(controls=[
                    ft.Text(f"Vender: {p['nombre']}", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Precio: {formatear_monto(p['precio'])} | Stock: {p['stock']}", color=ft.Colors.GREY_600),
                    ft.Divider(),
                    campo_cantidad, campo_medio,
                    ft.Row(controls=[
                        ft.Button("Cancelar", on_click=lambda e: page.pop_dialog(), expand=True),
                        ft.Button("Confirmar Venta", on_click=confirmar_venta, bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE, expand=True),
                    ], spacing=8)
                ]), bgcolor=ft.Colors.WHITE, padding=20, border_radius=20, width=ancho_dialogo()
            )
            page.show_dialog(ft.AlertDialog(content=contenido, actions=[]))

        filas = []
        for i, p in enumerate(productos):
            filas.append(
                ft.Container(
                    content=ft.Row(controls=[
                        ft.Column(controls=[
                            ft.Text(p["nombre"], weight=ft.FontWeight.BOLD, size=14),
                            ft.Text(f"Stock: {p['stock']} | {formatear_monto(p['precio'])}", size=11, color=ft.Colors.GREY_600),
                        ], spacing=2, expand=True),
                        ft.IconButton(ft.Icons.SHOPPING_CART, icon_color=ft.Colors.GREEN_600, on_click=lambda e, idx=i: vender_producto(idx)),
                    ]),
                    bgcolor=ft.Colors.GREY_50, padding=10, border_radius=10, margin=ft.Margin.only(bottom=5),
                )
            )

        contenido = ft.Container(
            content=ft.Column(controls=[
                ft.Text("Selecciona un producto para vender", size=16, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Column(controls=filas, scroll=ft.ScrollMode.AUTO, height=300),
                ft.Divider(),
                ft.Button("Cancelar", on_click=lambda e: page.pop_dialog(), expand=True)
            ]), bgcolor=ft.Colors.WHITE, padding=20, border_radius=20, width=ancho_dialogo()
        )
        page.show_dialog(ft.AlertDialog(content=contenido, actions=[]))

    # =========================================================
    # PANTALLA DE VENTAS (HISTORIAL)
    # =========================================================
    def abrir_ventas(e):
        page.controls.clear()
        total_hoy = sum(v["monto"] for v in ventas)

        def lista_ventas():
            if not ventas:
                return ft.Text("No hay ventas registradas aún.", color=ft.Colors.GREY_600)
            filas = []
            for v in reversed(ventas):
                filas.append(
                    ft.Container(
                        content=ft.Row(controls=[
                            ft.Icon(ft.Icons.SHOPPING_BAG, color=ft.Colors.GREEN_600),
                            ft.Column(controls=[
                                ft.Text(v["descripcion"], weight=ft.FontWeight.BOLD, size=13),
                                ft.Text(f"{v['fecha']} | {v['medio']}", size=10, color=ft.Colors.GREY_500),
                            ], spacing=2, expand=True),
                            ft.Text(formatear_monto(v["monto"]), weight=ft.FontWeight.BOLD),
                        ]), padding=10, bgcolor=ft.Colors.WHITE, border_radius=10, margin=ft.Margin.only(bottom=5)
                    )
                )
            return ft.Column(controls=filas)

        contenido_ventas = ft.Column(
            controls=[
                ft.Container(content=ft.Text("Ventas", size=26, weight=ft.FontWeight.BOLD), padding=20),
                ft.Container(
                    content=ft.Column(controls=[
                        ft.Text("Total histórico", size=13, color=ft.Colors.GREY_700),
                        ft.Text(formatear_monto(total_hoy), size=28, weight=ft.FontWeight.BOLD),
                    ]),
                    bgcolor=ft.Colors.PINK_50, padding=20, border_radius=20, margin=ft.Margin.only(left=20, right=20, bottom=20)
                ),
                ft.Container(content=lista_ventas(), padding=ft.Padding.only(left=20, right=20)),
                ft.Container(height=100)
            ], scroll=ft.ScrollMode.AUTO, expand=True,
        )

        boton_mas = ft.Container(
            content=ft.Icon(ft.Icons.ADD, size=32, color=ft.Colors.WHITE), bgcolor=ft.Colors.ORANGE_700,
            width=65, height=65, border_radius=50, alignment=ft.Alignment.CENTER,
            on_click=abrir_registrar_venta, ink=True, bottom=25, left=0, right=0
        )

        def item_nav(icono, titulo, accion, activo=False):
            return ft.Container(
                content=ft.Column(controls=[
                    ft.Icon(icono, size=24, color=ft.Colors.ORANGE_700 if activo else ft.Colors.GREY_500),
                    ft.Text(titulo, size=10, color=ft.Colors.ORANGE_700 if activo else ft.Colors.GREY_600),
                ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=8, on_click=accion, ink=True, expand=True,
            )

        barra_nav = ft.Container(
            content=ft.Row(controls=[
                item_nav(ft.Icons.HOME, "Inicio", lambda e: mostrar_app_principal()),
                item_nav(ft.Icons.PEOPLE, "Fiados", abrir_cartera),
                ft.Container(width=70),
                item_nav(ft.Icons.BAR_CHART, "Ventas", lambda e: None, activo=True),
                item_nav(ft.Icons.MENU, "Menú", abrir_menu),
            ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
            bgcolor=ft.Colors.WHITE, padding=8, bottom=0, left=0, right=0
        )

        page.add(ft.Stack(controls=[
            ft.Column(controls=[contenido_ventas], expand=True),
            boton_mas, barra_nav
        ], expand=True))
        page.update()

    # =========================================================
    # SALUD DE TU NEGOCIO
    # =========================================================
    def abrir_salud_negocio(e):
        page.controls.clear()
        total_ventas = len(ventas)
        dias_registrados = len(set(v["fecha"].split(" ")[0] for v in ventas)) if ventas else 0
        total_productos = len(productos)

        encabezado = ft.Container(
            content=ft.Row(controls=[
                ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: mostrar_app_principal()),
                ft.Text("Salud de tu negocio", size=24, weight=ft.FontWeight.BOLD),
            ]), padding=20
        )

        seccion_registros = ft.Container(
            content=ft.Row(controls=[
                ft.Column(controls=[ft.Text(str(dias_registrados), size=24, weight=ft.FontWeight.BOLD), ft.Text("días", size=10)], expand=True),
                ft.Column(controls=[ft.Text(str(total_ventas), size=24, weight=ft.FontWeight.BOLD), ft.Text("ventas", size=10)], expand=True),
                ft.Column(controls=[ft.Text(str(total_productos), size=24, weight=ft.FontWeight.BOLD), ft.Text("productos", size=10)], expand=True),
            ]), bgcolor=ft.Colors.WHITE, padding=20, border_radius=20, margin=20
        )

        page.add(ft.Column(controls=[encabezado, seccion_registros]))
        page.update()

    # =========================================================
    # MENÚ
    # =========================================================
    def abrir_menu(e):
        contenido = ft.Container(
            content=ft.Column(controls=[
                ft.Row(controls=[
                    ft.Container(content=ft.Icon(ft.Icons.MENU, color=ft.Colors.WHITE, size=26),
                                 bgcolor=ft.Colors.ORANGE_700, padding=10, border_radius=50),
                    ft.Text("Menú", size=18, weight=ft.FontWeight.BOLD, expand=True),
                ], spacing=10),
                ft.Divider(),
                ft.Container(
                    content=ft.Row(controls=[
                        ft.Icon(ft.Icons.INVENTORY, color=ft.Colors.BLACK_87),
                        ft.Text("Inventario", size=15, weight=ft.FontWeight.BOLD, expand=True),
                    ]),
                    padding=10, bgcolor=ft.Colors.GREY_100, border_radius=10,
                    on_click=lambda e: (page.pop_dialog(), abrir_inventario(None)), ink=True
                ),
                ft.Container(height=5),
                ft.Container(
                    content=ft.Row(controls=[
                        ft.Icon(ft.Icons.STORE, color=ft.Colors.BLACK_87),
                        ft.Text("Ajustes del Negocio", size=15, weight=ft.FontWeight.BOLD, expand=True),
                    ]),
                    padding=10, bgcolor=ft.Colors.GREY_100, border_radius=10,
                    on_click=lambda e: (page.pop_dialog(), abrir_ajustes(None)), ink=True
                ),
                ft.Container(height=15),
                ft.Button("Cerrar", on_click=lambda e: page.pop_dialog(), expand=True),
            ]),
            bgcolor=ft.Colors.WHITE, padding=20, border_radius=20, width=ancho_dialogo(),
        )
        page.show_dialog(ft.AlertDialog(content=contenido, actions=[]))

    # =========================================================
    # PANTALLA PRINCIPAL
    # =========================================================
    texto_total = None
    texto_subtitulo_total = None

    def mostrar_app_principal():
        nonlocal texto_total, texto_subtitulo_total
        page.controls.clear()

        encabezado = ft.Container(
            content=ft.Column(controls=[
                ft.Text(f"Hola, {datos_negocio['nombre']} 👋", size=22, weight=ft.FontWeight.BOLD),
                ft.Text(f"{datos_negocio['nombre']} - {datos_negocio['tipo']}", size=12, color=ft.Colors.GREY_600),
            ]), padding=15, margin=ft.Margin.only(top=12)
        )

        texto_total = ft.Text(formatear_monto(sum(f["monto"] for f in fiados)), color=ft.Colors.WHITE, size=30, weight=ft.FontWeight.BOLD)
        texto_subtitulo_total = ft.Text(f"{len(fiados)} fiado(s) pendiente(s)" if fiados else "Tu cartera está al día", color=ft.Colors.WHITE_70, size=13)

        main_card = ft.Container(
            content=ft.Column(controls=[
                ft.Text("Total por cobrar", color=ft.Colors.WHITE, size=14, weight=ft.FontWeight.BOLD),
                texto_total, texto_subtitulo_total,
                ft.Row(controls=[ft.Text("Ver lista", color=ft.Colors.WHITE, size=11), ft.Icon(ft.Icons.ARROW_FORWARD, color=ft.Colors.WHITE, size=14)], alignment=ft.MainAxisAlignment.END),
            ]),
            gradient=ft.LinearGradient(colors=["#FF5722", "#FFC107"]), padding=20, border_radius=20,
            margin=ft.Margin.only(left=12, right=12, top=8), on_click=abrir_cartera, ink=True
        )

        start_button = ft.Container(
            content=ft.Row(controls=[
                ft.Icon(ft.Icons.FAVORITE, color=ft.Colors.PINK_400),
                ft.Column(controls=[ft.Text("SALUD DE TU NEGOCIO", size=10, color=ft.Colors.PINK_700), ft.Text("Ver registros", size=15, weight=ft.FontWeight.BOLD)], expand=True),
            ]),
            bgcolor=ft.Colors.WHITE, padding=15, border_radius=15, margin=ft.Margin.only(left=12, right=12, top=10), on_click=abrir_salud_negocio
        )

        boton_mas = ft.Container(
            content=ft.Icon(ft.Icons.ADD, size=32, color=ft.Colors.WHITE), bgcolor=ft.Colors.ORANGE_700,
            width=65, height=65, border_radius=50, alignment=ft.Alignment.CENTER, on_click=abrir_registrar_fiado, ink=True, bottom=25, left=0, right=0
        )

        def item_nav(icono, titulo, accion, activo=False):
            return ft.Container(
                content=ft.Column(controls=[
                    ft.Icon(icono, size=24, color=ft.Colors.ORANGE_700 if activo else ft.Colors.GREY_500),
                    ft.Text(titulo, size=10, color=ft.Colors.ORANGE_700 if activo else ft.Colors.GREY_600),
                ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER), padding=8, on_click=accion, ink=True, expand=True
            )

        barra_nav = ft.Container(
            content=ft.Row(controls=[
                item_nav(ft.Icons.HOME, "Inicio", lambda e: None, activo=True),
                item_nav(ft.Icons.PEOPLE, "Fiados", abrir_cartera),
                ft.Container(width=70),
                item_nav(ft.Icons.BAR_CHART, "Ventas", abrir_ventas),
                item_nav(ft.Icons.MENU, "Menú", abrir_menu),
            ]), bgcolor=ft.Colors.WHITE, padding=8, bottom=0, left=0, right=0
        )

        page.add(ft.Stack(controls=[
            ft.Column(controls=[encabezado, main_card, start_button], expand=True, scroll=ft.ScrollMode.AUTO),
            boton_mas, barra_nav
        ], expand=True))
        page.update()

    # Iniciar
    mostrar_app_principal()

ft.run(main)
