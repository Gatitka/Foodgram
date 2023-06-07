from rest_framework import status
from rest_framework.response import Response


def check_existance_create_delete(model, method, response,
                                  serializer=None, instance=None,
                                  **kwargs):
    if method == 'POST':
        if model.objects.filter(**kwargs).exists():
            return Response('Данная запись уже существует.',
                            status=status.HTTP_400_BAD_REQUEST)
        model.objects.create(**kwargs)
        if response == 'response':
            return Response(serializer(instance).data)
        return 'redirect'

    if not model.objects.filter(**kwargs).exists():
        return Response('Такой записи нет, удаление невозможно.',
                        status=status.HTTP_400_BAD_REQUEST)
    model.objects.filter(**kwargs).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


if __name__ == '__main__':
    pass
