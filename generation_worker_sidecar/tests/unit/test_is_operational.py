import asyncio

import pytest

from utils import HealthCheckFailed, all_checks_successful


async def mock_check(throw_exception=False):
    await asyncio.sleep(1)
    if throw_exception:
        raise HealthCheckFailed("The mock check failed")
    return True


async def check_that_succeeds_on_second_try():
    if not hasattr(check_that_succeeds_on_second_try, "has_run"):
        check_that_succeeds_on_second_try.has_run = True
        raise Exception("Check failed on first try")
    return True


@pytest.mark.asyncio
async def test_all_checks_successful():
    checks = [lambda: mock_check(), lambda: mock_check()]
    assert await all_checks_successful(checks) is True


@pytest.mark.asyncio
async def test_check_fails():
    with pytest.raises(HealthCheckFailed):
        checks = [lambda: mock_check(), lambda: mock_check(True)]
        await all_checks_successful(checks)


@pytest.mark.asyncio
async def test_check_succeeds_on_retry():
    checks = [lambda: check_that_succeeds_on_second_try()]
    assert await all_checks_successful(checks) is True
