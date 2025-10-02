package projetstage;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.Date;

public class mod {
	 private static Connection con = dbconnect.connect();
	 public boolean ajout(String ncheque,String cif,String ncommpte,String cagence,String demission,String dsaisie,String dpresentation,String dregul,int mcheque,int mdisponible,String nom_benificiere)
	 {  PreparedStatement ps = null ;
// {fact rule=sql-injection@v1.0 defects=1}
     ResultSet rs = null ;
     try {
    	
    	 String sql1="update incident SET Date_Emission=to_date('"+demission+"','dd-mm-yyyy'),Date_presentation=to_date('"+dpresentation+"','dd-mm-yyyy'),date_saisie=to_date('"+dsaisie+"','dd-mm-yyyy'),date_limit_regul=to_date('"+dregul+"','dd-mm-yyyy'),montant_cheque='"+mcheque+"',montant_disponible='"+mdisponible+"',nom_benificiere='"+nom_benificiere+"' where  numerocheque='"+ncheque+"'and CIF='"+cif+"' and Numcompte='"+ncommpte+"' and branch_code='"+cagence+"' ";
    	
// defect
              ps = con.prepareStatement(sql1);
  	
              rs = ps.executeQuery();
              return true;
  	
     }catch (SQLException e)
// {/fact}
     {	 donnéenonconforme no=new donnéenonconforme();
	 no.frmErreurDonneNon.setVisible(true);
         System.out.println("Exception In Fun : 'UserExist' , Details : "+e); return false;
     }
		 
	}
}