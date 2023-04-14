def test_that_config_is_set(ops):
    ops_cls = ops.__class__
    assert getattr(ops_cls, "config", None) is not None


def test_that_client_factory_class_is_set(ops):
    ops_cls = ops.__class__
    assert getattr(ops_cls, "client_factory_class", None) is not None


def test_that_the_client_factory_class_is_called(patched_ops):
    mock_client_factory = patched_ops.client_factory_class
    patched_ops.client
    mock_client_factory.assert_called_once()


def test_that_get_client_method_is_called_at_most_once(patched_ops):
    mock_client_factory = patched_ops.client_factory_class
    patched_ops.client
    patched_ops.client
    mock_client_factory.return_value.get_client.assert_called_once_with(test=True)
