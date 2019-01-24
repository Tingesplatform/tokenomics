def test_address_generation(account):
    assert len(account.address) == 42
    assert account.address[0:2] == '0x'

    for c in account.address[2:]:
        assert c in 'abcdef1234567890'


def test_string_representation(account):
    assert str(account) == f'Account {account.address}'
