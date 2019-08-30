from django.conf import settings
from django.template import Context
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage, EmailMultiAlternatives


class Mailer():
    def __init__(self, to, data, temp_html, temp_txt):
        self.to = to
        self.data = data
        self.temp_html = temp_html
        self.temp_txt = temp_txt

    def noty_senhas(self):
        try:
            #to = kwargs.get('email')
            plainhtml = get_template(self.temp_html)
            plaintext = get_template(self.temp_txt)
            from_email = settings.SUPPORT_FROM_EMAIL  # NOREPLY_FROM_EMAIL
            #data = {'code': kwargs.get('code'), 'last_name': kwargs.get('last_name')}
            text_content = plaintext.render(self.data)
            html_content = plainhtml.render(self.data)  # render_to_string('senhas/email.txt', data) #
            msg = EmailMultiAlternatives("Recuperação de senha", text_content, from_email=from_email, to=[self.to, ])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            return None
        except Exception as ex:
            print(ex)
            return None

    def noty_planos(self):
        plainhtml = get_template(self.temp_html)
        plaintext = get_template(self.temp_txt)
        from_email = settings.NOREPLY_FROM_EMAIL  # NOREPLY_FROM_EMAIL
        text_content = plaintext.render(self.data)
        html_content = plainhtml.render(self.data)  # render_to_string('senhas/email.txt', data) #
        msg = EmailMultiAlternatives("URGENTE: Vencimento do seu plano", text_content, from_email=from_email, to=[self.to, ])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return None

    def noty_denuncia(self):
        plainhtml = get_template(self.temp_html)
        plaintext = get_template(self.temp_txt)
        from_email = settings.NOREPLY_FROM_EMAIL #DEFAULT_FROM_EMAIL  # NOREPLY_FROM_EMAIL
        text_content = plaintext.render(self.data)
        html_content = plainhtml.render(self.data)  # render_to_string('senhas/email.txt', data) #
        msg = EmailMultiAlternatives("ALERTA: DENUNCIA FEITA", text_content, from_email=from_email,
                                     to=[self.to, ])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return None

    def noty_sem_perfil(self):
        plainhtml = get_template(self.temp_html)
        plaintext = get_template(self.temp_txt)
        from_email = settings.NOREPLY_FROM_EMAIL #DEFAULT_FROM_EMAIL
        text_content = plaintext.render(self.data)
        html_content = plainhtml.render(self.data)  # render_to_string('senhas/email.txt', data) #
        msg = EmailMultiAlternatives("ALERTA: CRIEE SEUS ANÚNCIOS", text_content, from_email=from_email,
                                     to=[self.to, ])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return None

    def noty_sem_subs(self):
        plainhtml = get_template(self.temp_html)
        plaintext = get_template(self.temp_txt)
        from_email = settings.DEFAULT_FROM_EMAIL  # NOREPLY_FROM_EMAIL
        text_content = plaintext.render(self.data)
        html_content = plainhtml.render(self.data)  # render_to_string('senhas/email.txt', data) #
        msg = EmailMultiAlternatives("ALERTA: COLOQUE SEUS ANÚNCIOS NO AR", text_content, from_email=from_email,
                                     to=[self.to, ])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return None

    def noty_credito_acabando(self):
        plainhtml = get_template(self.temp_html)
        plaintext = get_template(self.temp_txt)
        from_email = settings.DEFAULT_FROM_EMAIL  # NOREPLY_FROM_EMAIL
        text_content = plaintext.render(self.data)
        html_content = plainhtml.render(self.data)  # render_to_string('senhas/email.txt', data) #
        msg = EmailMultiAlternatives("ALERTA: CRÉDITO ACABANDO", text_content, from_email=from_email,
                                     to=[self.to, ])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return None

