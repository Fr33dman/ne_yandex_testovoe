def set_assignee(login) // логин сотрудника поддержки
{
    // request_data - интерфейс управления БД. Считать, что не может исполняться несколько операций с БД параллельно

    requests = request_data.get_all() // получаем все обращения пользователей из БД
    request = requests.groupBy{ // Группирует по id (это че? группировка по уникальному полю? ладно, может имели ввиду uuid)
        it.id
    }.collect{ key, value ->  // Из каждой группы queryset возьмет те где version максимален
        value.max{it.version}
    }.findAll{ req ->  // Фильтрует чтобы сообщение было открыто и готово к обработке
        req.status == 'opened' &&
        req.state == 'ready'
    }.max{  // Берет обращение с максимальным приоритетом вроде
        it.priority
    }
    if (request == null)
        return null

    // По сути коллизий быть не должно, тк мы берем из групп id тот что с максимальным version, а если
    // обращение уже попало в обработку, то он будет автоматически со статусом inprogress, тк мы
    // когда создаем новый instance мы апаем версию, то есть на после 10 строчки у нас уже не должно быть коллизий.
    // Значит проблема в транзакциях - операции выполнились одновременно, значит добавим доп проверку на этот случай
    // и будем перезапускать функцию

    // -------------------------------------------------------------

    exists = request_data.get_all().findAll{ req ->
                                        req.id == request.id &&
                                        req.state == 'inprogress'
                                        }
    if (exists != null)
        return set_assignee(login)

    // -------------------------------------------------------------

    request.state = 'inprogress'
    request.assignee = login
    request.version += 1
    request_data.upload(request) // загружаем новую версию обращения в БД (старая не удаляется)
    return request
}