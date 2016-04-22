from smtplib import SMTP


msg = '''From: <test@blackhole.io>
To: <test@blackhole.io>
Subject: Test email
X-Blackhole-Mode: bounce

asdgrs\ghwrhyryhdhtjhetjrjtkdfgoihsegoineigeipngwghrhyehrehrehreherheherherherh
asdgrs\ghwrhyryhdhtjhetjrjtkdfgoihsegoineigeipngwghrhyehrehrehreherheherherherh
asdgrs\ghwrhyryhdhtjhetjrjtkdfgoihsegoineigeipngwghrhyehrehrehreherheherherherh
asdgrs\ghwrhyryhdhtjhetjrjtkdfgoihsegoineigeipngwghrhyehrehrehreherheherherherh
asdgrs\ghwrhyryhdhtjhetjrjtkdfgoihsegoineigeipngwghrhyehrehrehreherheherherherh
asdgrs\ghwrhyryhdhtjhetjrjtkdfgoihsegoineigeipngwghrhyehrehrehreherheherherherh
asdgrs\ghwrhyryhdhtjhetjrjtkdfgoihsegoineigeipngwghrhyehrehrehreherheherherherh
asdgrs\ghwrhyryhdhtjhetjrjtkdfgoihsegoineigeipngwghrhyehrehrehreherheherherherh

Random test email. Some UTF-8 characters: ßæøþ'''


smtp = SMTP('localhost', 1025)
# smtp = SMTP('blackhole.io', 25)
smtp.set_debuglevel(1)
smtp.login('a', 'b')
# smtp.starttls()
smtp.sendmail('test@blackhole.io', 'test@blackhole.io',
              msg.encode('utf-8'))
smtp.quit()
