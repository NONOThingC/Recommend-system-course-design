using System;
using System.Collections.Generic;
using System.Web;
using System.Web.UI;
using System.Web.UI.WebControls;
using System.Data.SqlClient;
using System.Configuration;
using MySql.Data.MySqlClient;

public partial class _Default : System.Web.UI.Page
{
    public MySqlConnection GetConn()
    {
        string constr = ConfigurationManager.AppSettings["connstring"].ToString();
        MySqlConnection myconn = new MySqlConnection(constr);
        return myconn;
    }
    protected void Page_Load(object sender, EventArgs e)
    {
    }
    protected void btn_Brow_Click(object sender, EventArgs e)
    {
        MySqlConnection myconn = GetConn();
        myconn.Open();
        string strsql = "select * from test";
        MySqlCommand cmd = new MySqlCommand(strsql, myconn);
        MySqlDataReader dr = cmd.ExecuteReader();
        while(dr.Read())
        {
            Response.Write(dr[0].ToString() + "<br>");
        }
        myconn.Close();
    }
    protected void btn_Add_Click(object sender, EventArgs e)
    {
        MySqlConnection myconn = GetConn();
        myconn.Open();
        string strsql = "insert into test values('" + TextBox1.Text + "','" + TextBox2.Text + "','" + TextBox3.Text + "')";
        MySqlCommand cmd = new MySqlCommand(strsql, myconn);
        //int k = cmd.ExecuteNonQuery();
        //Response.Write(k+"<br>");
        if (cmd.ExecuteNonQuery() > 0)
        {
            Response.Write("添加成功");
            TextBox1.Text = "";
            TextBox2.Text = "";
            TextBox3.Text = "";
        }
        else
        {
            Response.Write("添加失败");
        }
        myconn.Close();
    }
    protected void btn_Del_Click(object sender, EventArgs e)
    {
        if (TextBox1.Text != "")
        {
            MySqlConnection myconn = GetConn();
            myconn.Open();
            string strsql = "delete from test where id='" + TextBox1.Text + "'";
            MySqlCommand cmd = new MySqlCommand(strsql, myconn);
            if (cmd.ExecuteNonQuery() > 0)
            {
                cmd.Dispose();
                Response.Write("删除" + TextBox1.Text + "成功");
                TextBox1.Text = "";
                TextBox2.Text = "";
                TextBox3.Text = "";
            }
            else
            {
                Response.Write("删除失败");
            }
        }
        else{
            Response.Write("请输入ID");
        }
    }
}