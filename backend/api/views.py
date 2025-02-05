# from djoser.views import TokenCreateView, TokenDestroyView
# from rest_framework.response import Response
# from rest_framework.authtoken.models import Token
# from rest_framework import status
#
#
# class CustomTokenCreateView(TokenCreateView):
#     def create(self, request, *args, **kwargs):
#         response = super().create(request, *args, **kwargs)
#         return Response(
#             {"auth_token": response.data['auth_token']}, status=status.HTTP_200_OK
#         )
#
# # class CustomTokenDestroyView(TokenDestroyView):
# #     Token.key
# #     def post(self, request, *args, **kwargs):
# #         token = request.auth  # Это скорее всего строка, а не объект Token
# #         if token:
# #             try:
# #                 # Попробуем получить объект Token по строковому значению
# #                 Token.objects.get(key=token).delete()
# #                 return Response(status=status.HTTP_204_NO_CONTENT)
# #             except Token.DoesNotExist:
# #                 return Response(status=status.HTTP_400_BAD_REQUEST)
# #
# #         return Response(status=status.HTTP_400_BAD_REQUEST)