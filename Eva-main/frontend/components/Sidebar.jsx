import {
  Calendar,
  ChevronDown,
  ChevronUp,
  Home,
  Inbox,
  Plus,
  Projector,
  Search,
  Settings,
  User2,
} from "lucide-react";
import React from "react";
import Link from "next/link";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupAction,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuBadge,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuSub,
  SidebarSeparator,
} from "./ui/sidebar";
import {
  DropdownMenu,
  DropdownMenuItem,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "./ui/dropdown-menu";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "./ui/collapsible";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "../components/ui/dialog";

const items = [
  {
    title: "About EVA",
    icon: Home,
  },
];

async function AppSidebar() {
  return (
    <Sidebar collapsible="icon">
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton asChild>
              <Link href="/">
                <User2 />
                <span>Dhanush</span>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>

      <SidebarSeparator />
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Application</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {items.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <Dialog>
                    <DialogTrigger asChild>
                      <SidebarMenuButton>
                        <item.icon />
                        <span>{item.title}</span>
                      </SidebarMenuButton>
                    </DialogTrigger>

                    <DialogContent className="max-w-2xl">
                      <DialogHeader>
                        <DialogTitle className="text-2xl font-bold">
                          Meet EVA 🤖
                        </DialogTitle>
                        <DialogDescription>
                          EVA (Exploration and Vision Assistant) is a
                          multi-functional autonomous robot built for intelligent
                          navigation, perception, and task execution.
                        </DialogDescription>
                      </DialogHeader>

                      <div className="mt-4 grid md:grid-cols-2 gap-4">
                        <div className="p-4 border rounded-xl shadow-sm bg-card">
                          <h2 className="font-semibold text-lg mb-2">
                            Specifications
                          </h2>
                          <ul className="list-disc ml-5 text-sm space-y-1">
                            <li>Processor: NVIDIA Jetson Nano</li>
                            <li>Camera: Depth + Vision sensor</li>
                            <li>Mobility: 4-wheel omnidirectional drive</li>
                            <li>
                              Battery Life: 5 hours continuous operation
                            </li>
                          </ul>
                        </div>

                        <div className="p-4 border rounded-xl shadow-sm bg-card">
                          <h2 className="font-semibold text-lg mb-2">
                            Capabilities
                          </h2>
                          <ul className="list-disc ml-5 text-sm space-y-1">
                            <li>Real-time object detection & mapping</li>
                            <li>Autonomous path navigation</li>
                            <li>Remote manual control via dashboard</li>
                            <li>Data logging and analysis</li>
                          </ul>
                        </div>
                      </div>
                    </DialogContent>
                  </Dialog>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
        <Collapsible>
         
        </Collapsible>
      </SidebarContent>
      <SidebarFooter>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <SidebarMenuButton>
              <User2 />
              EVA <ChevronUp className="ml-auto" />
            </SidebarMenuButton>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem>Home Page</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </SidebarFooter>
    </Sidebar>
  );
}

export default AppSidebar;
