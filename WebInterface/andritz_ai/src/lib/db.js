import sql from 'mssql';

const config = {
  user: "teste",
  password: "Mpo69542507!",
  server: "localhost\\SQLEXPRESS",
  database: "UsersData",
  options: {
    encrypt: false,
    trustServerCertificate: true
  }
};

let pool = null;

async function connectToSqlServer() {
  if (pool && pool.connected) {
    return pool;
  }
  pool = await sql.connect(config);
  return pool;
}

export default connectToSqlServer