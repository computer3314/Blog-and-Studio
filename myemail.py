from django.core.mail import send_mail as core_send_mail
from django.core.mail import EmailMultiAlternatives
import threading
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)
class MyEmailThread(threading.Thread):
    """多線程，發送郵件"""
    def __init__(self, subject, body, from_email, recipient_list, fail_silently, html_message):
        threading.Thread.__init__(self)
        self.subject = subject
        self.body = body
        self.recipient_list = recipient_list
        self.from_email = from_email
        self.fail_silently = fail_silently
        self.html_message = html_message

    # 發送郵件
    def run(self):
        try:
            mail = EmailMultiAlternatives(self.subject, self.body, self.from_email, self.recipient_list)
            if self.html_message :
                mail.attach_alternative(self.html_message, 'text/html')
            return mail.send(self.fail_silently)
        except:
            logger.error("寄送失敗")

# 創建線程 start 啓動線程活動，會調用run方法
def my_send_mail(subject, body, from_email, recipient_list, fail_silently=False, html_message=None, *args, **kwargs):
    MyEmailThread(subject, body, from_email, recipient_list, fail_silently, html_message).start()