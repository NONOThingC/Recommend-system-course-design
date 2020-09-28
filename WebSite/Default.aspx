<%@ Page Language="C#" AutoEventWireup="true" CodeFile="Default.aspx.cs" Inherits="_Default" %>

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml">
<head runat="server">
    <title>我的网站</title>
</head>
<body>
    <form id="form1" runat="server">
    <asp:TextBox ID="TextBox1" runat="server" />
    <br />
    <asp:TextBox ID="TextBox2" runat="server" />
    <br />
    <asp:TextBox ID="TextBox3" runat="server" />
    <br />
    <asp:Button ID="Button3" Text="查询" runat="server" OnClick="btn_Brow_Click"/>
    &nbsp<asp:Button ID="Button1" Text="插入" runat="server" OnClick="btn_Add_Click"/>
    &nbsp<asp:Button ID="Button2" Text="删除" runat="server" OnClick="btn_Del_Click"/>
    </form>
</body>
</html>
