import httpx

def check_entity_fields(actual: dict, expected: dict, required_fields: set):
  missing_fields = required_fields - set(expected.keys())
  if missing_fields:
    if 'id' in missing_fields and 'in' not in expected:
      pass
    else:
      assert not missing_fields, f"❌ В expected отсутствуют ключи: {missing_fields}"

  for key in required_fields:
    assert actual[key] == expected[key], f"❌ Поле {key} не совпадает: {actual[key]} != {expected[key]}"


def check_entity_no_id(actual: dict, expected: dict, required_fields: set):
  check_entity_fields(actual, expected, required_fields - {'id'})


def check_entity(actual: dict, expected: dict, required_fields: set):
  check_entity_fields(actual, expected, required_fields)


def get_data(response: httpx.Response) -> dict:
  return response.json()['data']

# @todo - сделать более универсальной
def check_first_body_detail(response: dict, bad_field: str):
  assert 'detail' in response, "Ответ должен содержать ключ 'detail'"
  assert isinstance(response['detail'], list) and response['detail'], "Ответ 'detail' должен быть непустым списком"

  detail = response['detail'][0]  # Берем первую ошибку
  assert 'loc' in detail and isinstance(detail['loc'], list), "Ответ должен содержать поле 'loc' в detail"
  assert detail['loc'][0] == 'body', "Ошибка должна относиться к телу запроса"
  assert detail['loc'][1] == bad_field, f"Ожидалась ошибка в поле '{bad_field}', но получено '{detail['loc'][1]}'"


def assert_error(response: httpx.Response, status_code: list[int], bad_field: str):
  assert response.status_code in status_code, response.json()
  if response.status_code != httpx.codes.NOT_FOUND:
    check_first_body_detail(response.json(), bad_field)