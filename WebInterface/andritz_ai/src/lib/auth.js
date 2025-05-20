import bcrypt from 'bcryptjs';

async function verifyPassword(password, hashedPassword) {
  const isValid = await bcrypt.compare(password, hashedPassword);
  return isValid;
}

export default verifyPassword;