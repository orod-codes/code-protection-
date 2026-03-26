full_test_app — Python profile-style app. Run from THIS folder:

  python3 main.py

Layout:

  main.py
  models/user_profile.py
  services/collector.py
  services/reporter.py
  services/validator.py
  utils/formatters.py

Protect for customer:

  cd "/path/to/check-one"
  python3 engine.py full_test_app --generate-folder full_test_app_customer

Send only full_test_app_customer to your customer.
