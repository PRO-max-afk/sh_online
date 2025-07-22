import bcrypt

hashed = b"$2y$12$LuOIZGQ4j8bRC0gK2ZK/ieNe8L4pVRHRyBwEI/aQ1N.ENy./0IHXS"
password = b"your_password_here"

# توجه: اگر هش با $2y شروع میشه، bcrypt در پایتون مشکلی نداره؛ $2y هم‌ارز با $2b هست
if bcrypt.checkpw(password, hashed):
    print("✅ رمز صحیح است")
else:
    print("❌ رمز اشتباه است")
