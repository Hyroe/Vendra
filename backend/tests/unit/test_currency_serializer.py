from apps.stores.serializers import StoreCreateSerializer


def test_currency_serializer_case_insensitive():
    serializer = StoreCreateSerializer(data={"name": "X", "currency": "usd"})
    assert serializer.is_valid()
    assert serializer.validated_data["currency"] == "USD"


def test_currency_serializer_rejects_unsupported():
    serializer = StoreCreateSerializer(data={"name": "X", "currency": "JPY"})
    assert not serializer.is_valid()
    assert "currency" in serializer.errors
