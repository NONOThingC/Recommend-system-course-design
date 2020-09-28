using System;
using System.Collections.Generic;
using System.Web;
using System.Web.UI;
using System.Web.UI.WebControls;

public partial class Login : System.Web.UI.Page
{
    protected void Page_Load(object sender, EventArgs e)
    {
    }
    protected void btn_Login_Click(object sender, EventArgs e)
    {
        string userName = txtUserName.Text.Trim();
        string Pwd = txtUserPwd.Text.Trim();

        if ((txtUserName.Text == "jason" && txtUserPwd.Text == "123456") || (txtUserName.Text == "jack" && txtUserPwd.Text == "123456"))
        {
            Session.Timeout = 10;
            Session["userName"] = userName;
            this.Server.Transfer("Default.aspx");
        }
        else
        {
            Response.Write("用户名或密码错误");
        }
    }
    protected void btn_Reset_Click(object sender, EventArgs e)
    {
        txtUserName.Text = "";
        txtUserPwd.Text = "";
        txtUserName.Focus();
    }
    
}