// @ts-nocheck
import { Layout } from "antd";
import "./SideBar.css"
import SelectButton from "../SelectButton";
const SideBar = ({ menu, traceFolder, setTraceFolder }) => {

    console.log('sidebar render')

    return (
        <Layout.Sider
            className="sidebar"
            breakpoint={"lg"}
            theme="light"
            collapsedWidth={0}
            trigger={null}
        >
            {menu}
            <SelectButton traceFolder={traceFolder} setTraceFolder={setTraceFolder} />
        </Layout.Sider>
        
    );
};

export default SideBar;