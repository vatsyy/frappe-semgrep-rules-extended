import subprocess


def run_with_static_arguments():
	# ruleid: frappe-subprocess-exec
	return subprocess.run(["git", "status"], check=True)


def popen_with_validated_argument(validated_name):
	# ruleid: frappe-subprocess-exec
	return subprocess.Popen(["printf", "%s", validated_name])


def call_with_static_arguments():
	# ruleid: frappe-subprocess-exec
	return subprocess.call(["true"])


def check_call_with_static_arguments():
	# ruleid: frappe-subprocess-exec
	return subprocess.check_call(["git", "status"])


def check_output_with_static_arguments():
	# ruleid: frappe-subprocess-exec
	return subprocess.check_output(["git", "rev-parse", "HEAD"])


def run_through_shell(user_input):
	# ruleid: frappe-subprocess-shell-true
	return subprocess.run(f"printf '%s' {user_input}", shell=True)


def popen_through_shell(user_input):
	# ruleid: frappe-subprocess-shell-true
	return subprocess.Popen(user_input, shell=True)


def unrelated_function():
	# ok: frappe-subprocess-exec
	# ok: frappe-subprocess-shell-true
	return print("No external process")
