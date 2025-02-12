## Описание
Foodgram - проект посвященный рецептам.
Имеются возможности создания рецептов, подписки на пользователя, срздания и редак - 
тирования своего профиля.


- **запускается при выполнении команды git push**
- **tests:** проверка кода на соответствие PEP8.
- **build_and_push_to_docker_hub:** сборка и размещение образа проекта на DockerHub.
- **deploy:** автоматический деплой на боевой сервер и запуск проекта.
- **send_massage:** отправка уведомления пользователю в Телеграм.

#### После успешного результата работы workflow зайдите на Ваш сервер


- Заполните базу стартовыми данными содержащими игредиенты и несколько тэгов:

```bash
   sudo docker-compose exec backend python manage.py add_data
```

- Создайте суперпользователя:

```bash
   sudo docker-compose exec backend python manage.py createsuperuser
```

#### Примеры некоторых запросов API

Регистрация пользователя:

```bash
   POST /api/users/
```

Получение данных своей учетной записи:

```bash
   GET /api/users/me/ 
```

Добавление подписки:

```bash
   POST /api/users/id/subscribe/
```

Обновление рецепта:
  
```bash
   PATCH /api/recipes/id/
```


Проект доступен по адресу: <https://foodtastyborscht.bounceme.net>
