package me.CopyableCougar4.main;

import java.sql.*;

import org.bukkit.plugin.java.JavaPlugin;

public class MAPI extends JavaPlugin {
	
	/**
	 * Get a database connection
	 * @param ip
	 * @param database
	 * @param username
	 * @param password
	 * @return
	 */
	public static Connection getConnection(String ip, String database, String username, String password){
		
		String url = "jdbc:mysql://" + ip + ":3306/";
		String driver = "com.mysql.jdbc.Driver";
		try {
			Class.forName(driver).newInstance();
			return DriverManager.getConnection(url+database, username, password);
		} catch (InstantiationException | IllegalAccessException | ClassNotFoundException | SQLException e) {
			e.printStackTrace();
		}
		return null;
	    
	}
	
	public static void closeConnection(Connection conn) throws SQLException{
		conn.close();
	}
	
	/**
	 * Inserts records into a given database connection
	 * @param table
	 * @param columns --> any strings should be surrounded in single quotes
	 * @param values --> any strings should be surrounded in single quotes
	 * @param databaseConnection
	 */
	public static void insert(String table, Object[] columns, Object[] values, Connection databaseConnection){
		String cols = toString(columns);
		String value = toString(values);
		try {
			Statement st = databaseConnection.createStatement();
			st.executeQuery("INSERT INTO " + table + "(" + cols + ") VALUES (" + value + ")");
		} catch (SQLException e) {
			e.printStackTrace();
		}
	}
	
	public static String toString(Object[] array){
		String result = "";
		Integer count = 0;
		for(Object o : array){
			if(count == 0)
				result = (String)o;
			else
				result += ", " + (String)o;
			count++;
		}
		return result;
	}
	
	/**
	 * Selects a value from a database as an object. criteriaValue should be formatted as column>value
	 * @param databaseConnection
	 * @param column
	 * @param table
	 * @param criteriaValue
	 * @return
	 */
// {fact rule=sql-injection@v1.0 defects=1}
	public static Object select(Connection databaseConnection, String column, String table, String criteriaValue){
		String[] criteria = criteriaValue.split(">");
		Object result = null;
		try {
			Statement st = databaseConnection.createStatement();
// defect
			ResultSet rs = st.executeQuery("SELECT " + column + " FROM " + table + "WHERE " + criteria[0] + "='" + criteria[1] + "'");
			while(rs.next()){
				result = rs.getObject(column);
			}
		} catch (SQLException e) {
			e.printStackTrace();
// {/fact}
		}
		return result;
	}
	
	/**
	 * Updates a value in the database. criteria and change should be formatted as column>value
	 * @param databaseConnection
	 * @param table
	 * @param criteria
	 * @param change
	 * @return
	 */
	public static boolean update(Connection databaseConnection, String table, String criteria, String change){
		try {
			Statement st = databaseConnection.createStatement();
			String[] criteriaV = criteria.split(">");
			String[] update = change.split(">");
			st.executeUpdate("UPDATE " + table + " WHERE " + criteriaV[0] + "=" + criteriaV[1] + " SET "+ update[0] + "=" + update[1]);
			return true;
		} catch (SQLException e) {
			e.printStackTrace();
			return false;
		}
	}
	
	/**
	 * Deletes a record from a database
	 * @param databaseConnection
	 * @param table
	 * @param criteria
	 * @return
	 */
	public static boolean delete(Connection databaseConnection, String table, String criteria){
		String[] caseValue = criteria.split(">");
		try {
			Statement st = databaseConnection.createStatement();
			st.executeQuery("DELETE FROM " + table + " WHERE " + caseValue[0] + "=" + caseValue[1]);
			return true;
		} catch (SQLException e) {
			e.printStackTrace();
			return false;
		}
		
	}
	
	

}
