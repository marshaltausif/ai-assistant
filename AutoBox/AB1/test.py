def find_largest_number(arr):
  if not arr:
    return None
  largest = arr[0]
  for num in arr:
    if num > largest:
      largest = num
  return largest

# Example usage
my_array = [1, 5, 2, 8, 3]
largest_number = find_largest_number(my_array)
print(largest_number)