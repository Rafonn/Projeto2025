const sql = require('mssql');
const bcrypt = require('bcrypt');

const config = {
  user: 'teste',
  password: 'Mpo69542507!',
  server: 'localhost\\SQLEXPRESS',
  database: 'UsersData',
  options: {
    encrypt: false,
    trustServerCertificate: true
  }
};

async function insertUser(tableName, userData) {
  try {
    const saltRounds = 10;
    const hashedPassword = await bcrypt.hash(userData.PasswordHash, saltRounds);

    userData.PasswordHash = hashedPassword;

    const pool = await sql.connect(config);
    const req  = pool.request();

    Object.keys(userData).forEach(key => {
      req.input(key, userData[key]);
    });

    const cols   = Object.keys(userData).map(c => `[${c}]`).join(', ');
    const params = Object.keys(userData).map(c => `@${c}`).join(', ');
    const query  = `INSERT INTO ${tableName} (${cols}) VALUES (${params});`;

    const result = await req.query(query);
    console.log('Usuário inserido com sucesso:', result.rowsAffected);
  } catch (err) {
    console.error('Erro ao inserir usuário:', err);
    throw err;
  } finally {
    await sql.close();
  }
}

(async () => {
  const novoUsuario = {
    email: 'rafael.carneiro@andritz.com',
    PasswordHash: 'Mpo69542507!'
  };
  await insertUser('Users', novoUsuario);
})();
