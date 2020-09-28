<%@ Page Language="C#" AutoEventWireup="true" CodeFile="Login.aspx.cs" Inherits="Login" %>

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml">
<head runat="server">
    <title></title>
    <style type="text/css">
    .style1
    {
        height:23px;
     }
     .style2
     {
         height:25px;
         width:15px
     }
     </style>
</head>
<body>
    <form id="form1" runat="server">
    <asp:SiteMapPath ID="Site1" runat="server" />
    <div class="style1">
    </div>
    登陆界面<br />
    <asp:Label ID="Label1" runat="server" Text="用户名:" />
    <asp:TextBox ID="txtUserName" runat="server" Width="140px" />
    <br />
    <br />
    <asp:Label ID="Label2" runat="server" Text="密码：" />
    <asp:TextBox ID="txtUserPwd" runat="server" TextMode="password" Width="140px" />
    <br />
    <br />&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    <asp:Button ID="btn_Login" runat="server" OnClick="btn_Login_Click" Text="登陆" />&nbsp;&nbsp;&nbsp;
    <asp:Button ID="btn_Reset" runat="server" OnClick ="btn_Reset_Click" Text="重置" />
    </div>
    
    </form>
</body>
</html>
