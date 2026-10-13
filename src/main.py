import flet as ft
import urllib.parse

def main(page: ft.Page):
    page.title = "Fiado"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.scroll = ft.ScrollMode.AUTO
    page.bgcolor = ft.Colors.PINK_50

    # ====== DETECTAR SI ES MÓVIL ======
    def es_movil():
        return page.width is not None and page.width < 600

    # ====== ANCHO DINÁMICO PARA DIÁLOGOS ======
    def ancho_dialogo():
        ancho_pantalla = page.width if page.width else 400
        return min(ancho_pantalla * 0.9, 450)

    # ====== DATOS DEL NEGOCIO ======
    datos_negocio = {
        "nombre": "Mi Negocio",
        "tipo": "Bodega",
        "telefono": "",
        "direccion": "",
    }

    fiados = []

    # ====== ESTILOS DE BORDE ======
    def borde_naranja():
        return ft.OutlineInputBorder(side=ft.BorderSide(2, ft.Colors.ORANGE_400), border_radius=10)
    def borde_rosa():
        return ft.OutlineInputBorder(side=ft.BorderSide(2, ft.Colors.PINK_300), border_radius=10)
    def borde_verde():
        return ft.OutlineInputBorder(side=ft.BorderSide(2, ft.Colors.GREEN_400), border_radius=10)
    def borde_azul():
        return ft.OutlineInputBorder(side=ft.BorderSide(2, ft.Colors.BLUE_400), border_radius=10)

    # ====== FUNCIONES AUXILIARES ======
    def formatear_monto(valor):
        return "Bs. " + f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def abrir_whatsapp(numero, mensaje):
        numero_limpio = "".join(c for c in numero if c.isdigit())
        if numero_limpio.startswith("0"):
            numero_limpio = "58" + numero_limpio[1:]
        url = f"https://wa.me/{numero_limpio}?text={urllib.parse.quote(mensaje)}"
        page.launch_url(url)

    def refrescar_totales():
        total = sum(f["monto"] for f in fiados)
        texto_total.value = formatear_monto(total)
        if fiados:
            texto_subtitulo_total.value = f"{len(fiados)} fiado(s) pendiente(s)"
        else:
            texto_subtitulo_total.value = "Tu cartera está al día ✨"
        page.update()

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
                ft.Button("📋 Copiar mensaje", on_click=copiar, bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE),
                ft.Button("Cerrar", on_click=lambda e: page.pop_dialog()),
            ],
        ))

    # =========================================================
    # AJUSTES DEL NEGOCIO
    # =========================================================
    def abrir_ajustes(e):
        campo_nombre = ft.TextField(label="Nombre del negocio", value=datos_negocio["nombre"],
                                    border=borde_naranja())
        campo_tipo = ft.Dropdown(
            label="Tipo de negocio", value=datos_negocio["tipo"],
            options=[ft.dropdown.Option(t) for t in
                     ["Bodega", "Frutería", "Servicio Técnico", "Panadería",
                      "Farmacia", "Ferretería", "Otro"]],
            border_color=ft.Colors.ORANGE_400,
        )
        campo_telefono = ft.TextField(label="Teléfono del negocio", value=datos_negocio["telefono"],
                                      border=borde_naranja())
        campo_direccion = ft.TextField(label="Dirección", value=datos_negocio["direccion"],
                                       multiline=True, min_lines=2, max_lines=3, border=borde_naranja())

        def guardar(e):
            datos_negocio["nombre"] = campo_nombre.value or "Mi Negocio"
            datos_negocio["tipo"] = campo_tipo.value or "Bodega"
            datos_negocio["telefono"] = campo_telefono.value or ""
            datos_negocio["direccion"] = campo_direccion.value or ""
            subtitulo.value = f"{datos_negocio['nombre']} - {datos_negocio['tipo']}"
            info_negocio.value = f"📞 {datos_negocio['telefono']}  |  📍 {datos_negocio['direccion']}"
            page.pop_dialog()
            page.update()

        contenido = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(controls=[
                        ft.Container(content=ft.Icon(ft.Icons.STORE, color=ft.Colors.WHITE, size=28),
                                     bgcolor=ft.Colors.ORANGE_700, padding=10, border_radius=50),
                        ft.Text("Datos del Negocio", size=20, weight=ft.FontWeight.BOLD),
                    ], spacing=12),
                    ft.Divider(),
                    campo_nombre, campo_tipo, campo_telefono, campo_direccion,
                    ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
                    ft.Row(controls=[
                        ft.Button("Cancelar", on_click=lambda e: page.pop_dialog()),
                        ft.Button("Guardar", on_click=guardar, bgcolor=ft.Colors.ORANGE_700, color=ft.Colors.WHITE),
                    ], alignment=ft.MainAxisAlignment.END),
                ],
                spacing=10, scroll=ft.ScrollMode.AUTO,
            ),
            bgcolor=ft.Colors.WHITE, padding=20, border_radius=20, width=ancho_dialogo(),
            shadow=ft.BoxShadow(blur_radius=25, color=ft.Colors.with_opacity(0.3, ft.Colors.ORANGE_700)),
        )
        page.show_dialog(ft.AlertDialog(content=contenido, actions=[]))

    # =========================================================
    # REGISTRAR FIADO
    # =========================================================
    def abrir_registrar_fiado(e):
        campo_cliente = ft.TextField(label="Nombre del cliente", border=borde_rosa(), prefix_icon=ft.Icons.PERSON)
        campo_telefono_cliente = ft.TextField(label="Teléfono del cliente", border=borde_rosa(), prefix_icon=ft.Icons.PHONE)
        campo_monto = ft.TextField(label="Monto (Bs.)", hint_text="Ej: 4.500,50", border=borde_rosa(),
                                   prefix_icon=ft.Icons.ATTACH_MONEY)
        campo_fecha = ft.TextField(label="Fecha de pago", hint_text="Ej: 15/11/2026", border=borde_rosa(),
                                   prefix_icon=ft.Icons.CALENDAR_MONTH)
        campo_descripcion = ft.TextField(label="Descripción", hint_text="Ej: 2 harinas, 1 aceite",
                                         multiline=True, min_lines=2, max_lines=3, border=borde_rosa(),
                                         prefix_icon=ft.Icons.SHOPPING_BAG)

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
            refrescar_totales()
            page.pop_dialog()

        contenido = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(controls=[
                        ft.Container(content=ft.Icon(ft.Icons.ADD_CIRCLE, color=ft.Colors.WHITE, size=28),
                                     bgcolor=ft.Colors.PINK_700, padding=10, border_radius=50),
                        ft.Text("Registrar Fiado", size=20, weight=ft.FontWeight.BOLD),
                    ], spacing=12),
                    ft.Divider(),
                    campo_cliente, campo_telefono_cliente, campo_monto, campo_fecha, campo_descripcion,
                    ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
                    ft.Row(controls=[
                        ft.Button("Cancelar", on_click=lambda e: page.pop_dialog()),
                        ft.Button("Guardar", on_click=guardar_fiado, bgcolor=ft.Colors.PINK_700, color=ft.Colors.WHITE),
                    ], alignment=ft.MainAxisAlignment.END),
                ],
                spacing=10, scroll=ft.ScrollMode.AUTO,
            ),
            bgcolor=ft.Colors.WHITE, padding=20, border_radius=20, width=ancho_dialogo(),
            height=min(page.height * 0.85 if page.height else 600, 650),
            shadow=ft.BoxShadow(blur_radius=25, color=ft.Colors.with_opacity(0.3, ft.Colors.PINK_700)),
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
            page.pop_dialog()
            page.pop_dialog()
            abrir_cartera(None)

        contenido = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(controls=[
                        ft.Container(content=ft.Icon(ft.Icons.EDIT_CALENDAR, color=ft.Colors.WHITE, size=28),
                                     bgcolor=ft.Colors.BLUE_600, padding=10, border_radius=50),
                        ft.Text("Editar fecha", size=18, weight=ft.FontWeight.BOLD),
                    ], spacing=12),
                    ft.Divider(),
                    ft.Text(f"Cliente: {fiado['cliente']}", size=15, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Fecha actual: {fiado['fecha_pago'] or 'No definida'}", size=13, color=ft.Colors.GREY_600),
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    campo_nueva_fecha,
                    ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
                    ft.Row(controls=[
                        ft.Button("Cancelar", on_click=lambda e: page.pop_dialog()),
                        ft.Button("Guardar", on_click=guardar, bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE),
                    ], alignment=ft.MainAxisAlignment.END),
                ],
                spacing=10,
            ),
            bgcolor=ft.Colors.WHITE, padding=20, border_radius=20, width=ancho_dialogo(),
            shadow=ft.BoxShadow(blur_radius=25, color=ft.Colors.with_opacity(0.3, ft.Colors.BLUE_600)),
        )
        page.show_dialog(ft.AlertDialog(content=contenido, actions=[]))

    # =========================================================
    # REGISTRAR ABONO
    # =========================================================
    def registrar_abono(fiado):
        campo_abono = ft.TextField(label="Monto del abono (Bs.)", hint_text="Ej: 1.000,00",
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
                campo_abono.error_text = f"Excede el saldo ({formatear_monto(fiado['monto'])})"
                page.update()
                return

            fiado["abonado"] = fiado.get("abonado", 0.0) + abono_float
            fiado["monto"] = fiado["monto"] - abono_float

            if fiado["monto"] <= 0.01:
                page.pop_dialog()
                page.pop_dialog()
                eliminar_fiado(fiado, motivo="¡Fiado pagado completamente!")
                return

            page.pop_dialog()
            page.pop_dialog()
            refrescar_totales()
            abrir_cartera(None)

        contenido = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(controls=[
                        ft.Container(content=ft.Icon(ft.Icons.PAYMENTS, color=ft.Colors.WHITE, size=28),
                                     bgcolor=ft.Colors.GREEN_600, padding=10, border_radius=50),
                        ft.Text("Registrar abono", size=18, weight=ft.FontWeight.BOLD),
                    ], spacing=12),
                    ft.Divider(),
                    ft.Text(f"Cliente: {fiado['cliente']}", size=15, weight=ft.FontWeight.BOLD),
                    ft.Container(
                        content=ft.Column(controls=[
                            ft.Text(f"Saldo pendiente: {formatear_monto(fiado['monto'])}",
                                    size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_700),
                            ft.Text(f"Total original: {formatear_monto(fiado.get('monto_original', fiado['monto']))}",
                                    size=12, color=ft.Colors.GREY_600),
                            ft.Text(f"Ya abonado: {formatear_monto(fiado.get('abonado', 0))}",
                                    size=12, color=ft.Colors.GREEN_700),
                        ], spacing=3),
                        bgcolor=ft.Colors.GREY_100, padding=12, border_radius=10,
                    ),
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    campo_abono,
                    ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
                    ft.Row(controls=[
                        ft.Button("Cancelar", on_click=lambda e: page.pop_dialog()),
                        ft.Button("Abonar", on_click=guardar, bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE),
                    ], alignment=ft.MainAxisAlignment.END),
                ],
                spacing=8,
            ),
            bgcolor=ft.Colors.WHITE, padding=20, border_radius=20, width=ancho_dialogo(),
            shadow=ft.BoxShadow(blur_radius=25, color=ft.Colors.with_opacity(0.3, ft.Colors.GREEN_600)),
        )
        page.show_dialog(ft.AlertDialog(content=contenido, actions=[]))

    # =========================================================
    # ELIMINAR FIADO
    # =========================================================
    def eliminar_fiado(fiado, motivo=""):
        def confirmar(e):
            if fiado in fiados:
                fiados.remove(fiado)
            refrescar_totales()
            page.pop_dialog()
            try:
                page.pop_dialog()
            except Exception:
                pass
            abrir_cartera(None)

        titulo = motivo if motivo else "Eliminar fiado"

        contenido = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(controls=[
                        ft.Container(content=ft.Icon(ft.Icons.DELETE, color=ft.Colors.WHITE, size=28),
                                     bgcolor=ft.Colors.RED_600, padding=10, border_radius=50),
                        ft.Text(titulo, size=17, weight=ft.FontWeight.BOLD),
                    ], spacing=12),
                    ft.Divider(),
                    ft.Text(f"Cliente: {fiado['cliente']}", size=14),
                    ft.Text(f"Monto pendiente: {formatear_monto(fiado['monto'])}",
                            size=14, color=ft.Colors.ORANGE_700),
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    ft.Text("¿Eliminar este fiado?", size=14, color=ft.Colors.GREY_700),
                    ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
                    ft.Row(controls=[
                        ft.Button("Cancelar", on_click=lambda e: page.pop_dialog()),
                        ft.Button("Sí, eliminar", on_click=confirmar, bgcolor=ft.Colors.RED_600, color=ft.Colors.WHITE),
                    ], alignment=ft.MainAxisAlignment.END),
                ],
                spacing=8,
            ),
            bgcolor=ft.Colors.WHITE, padding=20, border_radius=20, width=ancho_dialogo(),
            shadow=ft.BoxShadow(blur_radius=25, color=ft.Colors.with_opacity(0.3, ft.Colors.RED_600)),
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
                    ft.Text("Aún no hay fiados registrados", size=16,
                            weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_700),
                    ft.Text("Toca 'Registrar nuevo fiado' para agregar el primero",
                            size=12, color=ft.Colors.GREY_500),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                padding=40,
            )
        else:
            filas = []
            for f in fiados:
                def crear_recordatorio(fiado=f):
                    def recordar(e):
                        msg = (f"Hola {fiado['cliente']}, le saluda {datos_negocio['nombre']}. "
                               f"Le recordamos que tiene un saldo pendiente de "
                               f"{formatear_monto(fiado['monto'])}")
                        if fiado.get('fecha_pago'):
                            msg += f" con fecha de pago para el {fiado['fecha_pago']}"
                        if fiado.get('descripcion'):
                            msg += f" ({fiado['descripcion']})"
                        msg += ". Agradecemos su pronto pago. ¡Gracias!"
                        if fiado.get('telefono'):
                            try:
                                abrir_whatsapp(fiado['telefono'], msg)
                            except Exception:
                                mostrar_mensaje_copiable("Mensaje de recordatorio", msg)
                        else:
                            mostrar_mensaje_copiable("Mensaje de recordatorio", msg)
                    return recordar

                abonado = f.get("abonado", 0.0)
                monto_original = f.get("monto_original", f["monto"])
                info_extra = f"  |  Abonado: {formatear_monto(abonado)}" if abonado > 0 else ""
                progreso = (abonado / monto_original) if monto_original > 0 else 0

                # En móvil, los botones se apilan
                if es_movil():
                    botones = ft.Column(
                        controls=[
                            ft.Button("💬 Recordar", on_click=crear_recordatorio(f),
                                      bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE, width=ancho_dialogo() * 0.85),
                            ft.Row(controls=[
                                ft.Button("💵 Abono", on_click=lambda e, fiado=f: registrar_abono(fiado),
                                          bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE, expand=True),
                                ft.Button("📅 Fecha", on_click=lambda e, fiado=f: editar_fecha(fiado),
                                          bgcolor=ft.Colors.ORANGE_600, color=ft.Colors.WHITE, expand=True),
                            ], spacing=5),
                            ft.Button("🗑️ Eliminar", on_click=lambda e, fiado=f: eliminar_fiado(fiado),
                                      bgcolor=ft.Colors.RED_600, color=ft.Colors.WHITE, width=ancho_dialogo() * 0.85),
                        ],
                        spacing=5,
                    )
                else:
                    botones = ft.Row(
                        controls=[
                            ft.Button("💬 Recordar", on_click=crear_recordatorio(f),
                                      bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE),
                            ft.Button("💵 Abono", on_click=lambda e, fiado=f: registrar_abono(fiado),
                                      bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE),
                            ft.Button("📅 Editar", on_click=lambda e, fiado=f: editar_fecha(fiado),
                                      bgcolor=ft.Colors.ORANGE_600, color=ft.Colors.WHITE),
                            ft.Button("🗑️ Eliminar", on_click=lambda e, fiado=f: eliminar_fiado(fiado),
                                      bgcolor=ft.Colors.RED_600, color=ft.Colors.WHITE),
                        ],
                        alignment=ft.MainAxisAlignment.END, spacing=6, wrap=True,
                    )

                filas.append(
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Row(controls=[
                                    ft.Container(content=ft.Icon(ft.Icons.PERSON, color=ft.Colors.WHITE, size=20),
                                                 bgcolor=ft.Colors.ORANGE_400, padding=8, border_radius=50),
                                    ft.Column(controls=[
                                        ft.Text(f["cliente"], weight=ft.FontWeight.BOLD, size=15),
                                        ft.Text(f["descripcion"] or "(sin descripción)", size=12,
                                                color=ft.Colors.GREY_600),
                                    ], spacing=2, expand=True),
                                    ft.Column(controls=[
                                        ft.Text("Pendiente:", size=10, color=ft.Colors.GREY_600),
                                        ft.Text(formatear_monto(f["monto"]), weight=ft.FontWeight.BOLD,
                                                color=ft.Colors.ORANGE_700, size=16),
                                    ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.END),
                                ]),
                                ft.Row(controls=[
                                    ft.Icon(ft.Icons.CALENDAR_MONTH, size=14, color=ft.Colors.GREY_500),
                                    ft.Text(f"Pago: {f['fecha_pago'] or 'No definida'}", size=11,
                                            color=ft.Colors.GREY_500),
                                ], spacing=5),
                                ft.Row(controls=[
                                    ft.Icon(ft.Icons.PHONE, size=14, color=ft.Colors.GREY_500),
                                    ft.Text(f"{f['telefono'] or 'Sin teléfono'}", size=11,
                                            color=ft.Colors.GREY_500),
                                ], spacing=5),
                                ft.Text(f"Original: {formatear_monto(monto_original)}{info_extra}",
                                        size=11, color=ft.Colors.GREY_500),
                                ft.ProgressBar(value=progreso, color=ft.Colors.GREEN_500,
                                               bgcolor=ft.Colors.GREY_300, height=6),
                                botones,
                            ],
                            spacing=8,
                        ),
                        bgcolor=ft.Colors.WHITE, padding=15, border_radius=15,
                        margin=ft.Margin.only(bottom=10),
                        shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK)),
                    )
                )
            contenido_lista = ft.Column(controls=filas, spacing=5)

        total = sum(f["monto"] for f in fiados)

        contenido = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(controls=[
                        ft.Container(content=ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET, color=ft.Colors.WHITE, size=26),
                                     bgcolor=ft.Colors.ORANGE_700, padding=10, border_radius=50),
                        ft.Column(controls=[
                            ft.Text("Cartera por cobrar", size=20, weight=ft.FontWeight.BOLD),
                            ft.Text(f"Total: {formatear_monto(total)}", size=15,
                                    weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_700),
                        ], spacing=2),
                    ], spacing=12),
                    ft.Divider(),
                    contenido_lista,
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    ft.Row(controls=[
                        ft.Button("Cerrar", on_click=lambda e: page.pop_dialog(),
                                  bgcolor=ft.Colors.ORANGE_700, color=ft.Colors.WHITE),
                    ], alignment=ft.MainAxisAlignment.END),
                ],
                spacing=10, scroll=ft.ScrollMode.AUTO,
            ),
            bgcolor=ft.Colors.WHITE, padding=20, border_radius=20,
            width=ancho_dialogo() if es_movil() else 550,
            height=min(page.height * 0.85 if page.height else 600, 680),
            shadow=ft.BoxShadow(blur_radius=25, color=ft.Colors.with_opacity(0.3, ft.Colors.ORANGE_700)),
        )
        page.show_dialog(ft.AlertDialog(content=contenido, actions=[]))

    # =========================================================
    # ENCABEZADO
    # =========================================================
    saludo = ft.Text("Hola, bienvenido a Fiado 👋", size=22 if es_movil() else 24,
                     weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
    subtitulo = ft.Text(f"{datos_negocio['nombre']} - {datos_negocio['tipo']}",
                        size=13, color=ft.Colors.WHITE_70)
    info_negocio = ft.Text("Configura tu negocio en el engranaje ⚙️",
                           size=11, color=ft.Colors.WHITE_70)

    boton_ajustes = ft.IconButton(icon=ft.Icons.SETTINGS, icon_color=ft.Colors.WHITE,
                                  icon_size=26, tooltip="Configurar negocio", on_click=abrir_ajustes)

    encabezado = ft.Container(
        content=ft.Row(
            controls=[
                ft.Column(controls=[saludo, subtitulo, info_negocio], spacing=4, expand=True),
                boton_ajustes,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.START,
        ),
        bgcolor=ft.Colors.ORANGE_700, padding=20, border_radius=20,
        margin=ft.Margin.only(left=15, right=15, top=15),
        shadow=ft.BoxShadow(blur_radius=20, color=ft.Colors.with_opacity(0.4, ft.Colors.ORANGE_700)),
    )

    # =========================================================
    # TARJETA NARANJA
    # =========================================================
    texto_total = ft.Text("Bs. 0,00", color=ft.Colors.WHITE,
                          size=28 if es_movil() else 32, weight=ft.FontWeight.BOLD)
    texto_subtitulo_total = ft.Text("Tu cartera está al día ✨", color=ft.Colors.WHITE_70, size=13)

    main_card = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(controls=[
                    ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET, color=ft.Colors.WHITE, size=26),
                    ft.Text("Total por cobrar", color=ft.Colors.WHITE, size=15, weight=ft.FontWeight.BOLD),
                ], spacing=8),
                ft.Divider(height=10, color=ft.Colors.WHITE_24),
                texto_total, texto_subtitulo_total,
                ft.Divider(height=5, color=ft.Colors.TRANSPARENT),
                ft.Row(controls=[
                    ft.Text("Ver lista completa", color=ft.Colors.WHITE, size=12, weight=ft.FontWeight.BOLD),
                    ft.Icon(ft.Icons.ARROW_FORWARD, color=ft.Colors.WHITE, size=16),
                ], alignment=ft.MainAxisAlignment.END),
            ],
            spacing=8,
        ),
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_LEFT, end=ft.Alignment.BOTTOM_RIGHT,
            colors=["#FF9800", "#F57C00", "#E65100"],
        ),
        padding=25, border_radius=20,
        margin=ft.Margin.only(left=15, right=15, top=15),
        on_click=abrir_cartera, ink=True,
        shadow=ft.BoxShadow(blur_radius=25, color=ft.Colors.with_opacity(0.5, ft.Colors.ORANGE_700)),
    )

    # =========================================================
    # BOTÓN REGISTRAR
    # =========================================================
    start_button = ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(content=ft.Icon(ft.Icons.ADD_CIRCLE, color=ft.Colors.WHITE, size=30),
                             bgcolor=ft.Colors.PINK_700, padding=12, border_radius=50),
                ft.Column(
                    controls=[
                        ft.Text("SALUD DE TU NEGOCIO", color=ft.Colors.PINK_700,
                                size=10, weight=ft.FontWeight.BOLD),
                        ft.Text("Registrar nuevo fiado", color=ft.Colors.BLACK_87,
                                size=16 if es_movil() else 18, weight=ft.FontWeight.BOLD),
                        ft.Text("Toca para anotar una venta, gasto o fiado.",
                                color=ft.Colors.GREY_700, size=12),
                    ],
                    spacing=3, expand=True,
                ),
                ft.Icon(ft.Icons.ARROW_FORWARD_IOS, color=ft.Colors.PINK_400, size=18),
            ],
            spacing=12,
        ),
        bgcolor=ft.Colors.WHITE, padding=18, border_radius=20,
        margin=ft.Margin.only(left=15, right=15, bottom=15),
        border=ft.Border(
            top=ft.BorderSide(2, ft.Colors.PINK_100),
            right=ft.BorderSide(2, ft.Colors.PINK_100),
            bottom=ft.BorderSide(2, ft.Colors.PINK_100),
            left=ft.BorderSide(2, ft.Colors.PINK_100),
        ),
        shadow=ft.BoxShadow(blur_radius=15, color=ft.Colors.with_opacity(0.2, ft.Colors.PINK_700)),
        on_click=abrir_registrar_fiado, ink=True,
    )

    # =========================================================
    # AGREGAR TODO
    # =========================================================
    page.add(encabezado, main_card, start_button)

ft.run(main)
