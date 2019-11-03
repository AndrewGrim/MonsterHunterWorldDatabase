import typing

def debug(variable: object, name: str = "None", message: str = "None") -> None: 
	"""
	variable = The variable you want to print out.

	name = The name of the variable, default is None. This is just to make it clear what variable the function is printing.
	"""
	
	try:
		typeVar = type(variable)
	except Exception as e:
		print("type:", e)
		typeVar = None

	try:
		length = len(variable)
	except Exception as e:
		print("length:", e)
		length = None

	try:
		content = ""
		if typeVar == dict:
			kl = 5
			vl = 7
			ktl = 0
			vtl = 0
			for k, v in variable.items():
				if len(str(k)) > kl:
					kl = len(str(k))
				if len(str(v)) > vl:
					vl = len(str(v))
				if len(str(type(k))) > ktl:
					ktl = len(str(type(k)))
				if len(str(type(v))) > vtl:
					vtl = len(str(type(v)))

			content += f"\n\t{'Key':^{kl}} {'<type>':^{ktl}}   {'Value':^{vl}} {'<type>':^{vtl}}\n"
			content += f"\t{'-' * (kl + vl + ktl + vtl + 5)}\n"
			for k, v in variable.items():
				content += f"\t{k:^{kl}} {str(type(k)):^{ktl}}   {v:^{vl}} {str(type(k)):^{vtl}}\n"

		elif typeVar == list or typeVar == tuple:
			il = 7
			vl = 7
			vtl = 0
			for i, item in enumerate(variable):
				if len(str(i)) > il:
					il = len(str(i))
				if len(str(item)) > vl:
					vl = len(str(item))
				if len(str(type(item))) > vtl:
					vtl = len(str(type(item)))

			content += f"\n\t{'Index':^{il}}   {'Value':^{vl}} {'<type>':^{vtl}}\n"
			content += f"\t{'-' * (il + vl + vtl + 4)}\n"
			for i, item in enumerate(variable):
				content += f"\t{i:^{il}}   {item:^{vl}} {str(type(item)):^{vtl}}\n"

		else:
			content = repr(variable)
	except Exception as e:
		print("content:", e)
		content = None

	print(f"\nMessage: {message}")
	print(f"Name: {name}")
	print(f"Type: {typeVar}")
	print(f"Length: {length}")
	print(f"Content: {content}")