// app/api/auth/[...nextauth]/route.js
import NextAuth from 'next-auth';
import CredentialsProvider from 'next-auth/providers/credentials';
import verifyPassword from '@/lib/auth';
import connectToSqlServer from '@/lib/db';
import * as sql from 'mssql';

export const authOptions = {
  debug: true,
  providers: [
    CredentialsProvider({
      id: 'credentials',
      name: 'Credentials',
      credentials: { email: { label: 'Email', type: 'email' }, password: { label: 'Senha', type: 'password' } },
      
      async authorize(credentials) {
        const pool = await connectToSqlServer();

        const result = await pool.request()
          .input('email', sql.VarChar(255), credentials.email)
          .query('SELECT Id, Email, PasswordHash FROM Users WHERE Email = @email');

        const user = result.recordset[0];

        if (!user) return null;

        const isValid = await verifyPassword(credentials.password, user.PasswordHash);

        if (!isValid) return null;

        return { email: user.Email };
      }
    })
  ],
  session: { strategy: 'jwt' },
  pages: { signIn: '/login', error: '/login' },
  callbacks: {
    async jwt({ token, user }) {
      if (user?.email) token.email = user.email;
      return token;
    },
    async session({ session, token }) {
      session.user.email = token.email;
      return session;
    }
  },
  secret: process.env.NEXTAUTH_SECRET,
};

const handler = NextAuth(authOptions);
export { handler as GET, handler as POST };
