from pkgutil import iter_modules

from orca import services as services_module


def test_that_all_implemented_services_are_being_tested(services):
    # Get list of implemented services that are being tested
    tested_services = set(services)

    # Get list of implemented services
    submodules = iter_modules(services_module.__path__)
    submodule_names = [x.name for x in submodules]
    # Ignore `base` submodule since it's not an implementation
    impl_services = {x for x in submodule_names if x != "base"}

    # Check that no implemented services are left untested
    assert not impl_services - tested_services
