Реалізація найпростішоого веб-додатоку.

Створено веб-додаток з маршрутизацією дляhtml сторінок: index.html та message.html та about_me.html.

Також:

Обробіть під час роботи програми статичні ресурси: style.css, logo.png;
Організуйте роботу з формою на сторінці message.html;
У разі виникнення помилки 404 Not Found повертайте сторінку error.html

Реалізований рендеринг сторінки about_me.html

Ваша програма працює на порту 3000
Для роботи з формою створіть Socket сервер на порту 5000. Алгоритм роботи такий. Ви вводите дані у форму, вони потрапляють у ваш веб-додаток, який пересилає його далі на обробку за допомогою socket (протокол UDP), Socket серверу. Socket сервер переводить отриманий байт-рядок у словник і зберігає його в json файл data.json в папку storage.
