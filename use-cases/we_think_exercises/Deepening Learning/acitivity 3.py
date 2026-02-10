def my_function(title, *args, **kwargs):
  
  print("Title:", title)
  print("Positional arguments:", args)
  print("Keyword arguments:", kwargs)

my_function("User Info", "Emil", "Thando", age = 20, city = "MSU")