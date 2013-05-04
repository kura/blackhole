.. _faq:

FAQ
===

Q. Why did you develop blackhole?

A. A few years ago I was tasked with designing a new send engine for an email platform for the company I worked for at the time.
   The current email send engine was written in PHP and was trigged via minutely CRON tasks and used Postfix for sending the mail
   out. It was not particularly fast and required a lot of servers to perform the task.

   The new send engine I was prototyping was written in Stackless Python using scheduling and microthreads and was able to generate
   and send email so fast that any server it was pointed at would buckle under the pressure.
   To test the full throughput of the prototype I needed a new approach to receiving the generated email as having a huge MTA pool
   using Postfix, Exim or Sendmail was simply not viable.

   SimpleMTA was born.

   SimpleMTA was a Python implementation of a Java standalone mail server I had found, it used Stackless Python and microthreads
   to receive and handle incoming mail. As the prototype evolved, so did SimpleMTA until it was eventually switched to use
   eventlet and greenlet and was released without license for anyone to use, modify etc.

   As time went on and the prototype was finished and the real work of writing a full fledged send engine was underway, I decided
   to familiarise myself with the Tornado framework more and test it's capabilities, that process evolved in to Blackhole.

   Blackhole existed for one purpose - like SimpleMTA - receive a whole lot of bulk email and respond with a set of defined SMTP
   codes. Sometimes we needed it to blindly accept all email, other times we needed it to bounce, respond that the server was
   offline or broken etc.

   And that takes us up to the current state of Blackhole.

   I have my own modified version of Blackhole that can do slightly more than the open-source product released here, it can read
   the mail, choose to accept it or bounce it based on user defined algorythms such as only accept 10% of all incoming email.
   It can choose to open the email, read it's contents, open up relevant transparent GIFs and PNGs to fool tracking systems in
   to thinking a real user has actually opened the email, as well as click on tracking links and browse around the web pages
   that are presented on those links being clicked.
   Sadly all of this functionality is very domain specific and will probably never be released, but it shows how Blackhole can
   be modified to do more than it currently does.


Q. Why Tornado?

A. As outlined in the question above, I wanted to learn Tornado and now the simplest answer is - why not?
